"""Memory scanner for hackmud game terminal output

Provides a clean API for reading terminal content from hackmud's memory.
Uses Mono vtables to locate Window objects and read TextMeshProUGUI text.
"""

import json
import struct
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Tuple

# Import config, exceptions, and config generator
try:
    from . import config
    from . import config_generator
    from .exceptions import (
        GameNotFoundError,
        ConfigError,
        MemoryReadError,
        WindowNotFoundError,
        OffsetsNotFoundError
    )
except ImportError:
    # Fallback for direct execution
    import config
    import config_generator
    from exceptions import (
        GameNotFoundError,
        ConfigError,
        MemoryReadError,
        WindowNotFoundError,
        OffsetsNotFoundError
    )


# Debug flag from environment
_DEBUG = os.getenv('HACKMUD_DEBUG', '').lower() in ('1', 'true', 'yes')

def _debug_print(*args, **kwargs):
    """Print debug message if DEBUG is enabled"""
    if _DEBUG:
        print('[DEBUG scanner]', *args, **kwargs)


# Memory reader protocol for dependency injection and testing
class MemoryReader(Protocol):
    """Protocol for memory reading - allows mocking in tests"""

    def open(self, pid: int) -> None:
        """Open memory access for process"""
        ...

    def close(self) -> None:
        """Close memory access"""
        ...

    def read(self, address: int, size: int) -> bytes:
        """Read bytes from memory address"""
        ...


class ProcMemReader:
    """Real memory reader using /proc/PID/mem"""

    def __init__(self):
        self.mem_file = None
        self.pid = None

    def open(self, pid: int) -> None:
        """Open /proc/PID/mem for reading"""
        self.pid = pid
        try:
            self.mem_file = open(f'/proc/{pid}/mem', 'rb', buffering=0)
        except (FileNotFoundError, PermissionError) as e:
            raise MemoryReadError(f"Cannot access process {pid} memory: {e}")

    def close(self) -> None:
        """Close memory file"""
        if self.mem_file:
            self.mem_file.close()
            self.mem_file = None

    def read(self, address: int, size: int) -> bytes:
        """Read bytes from memory address"""
        if not self.mem_file:
            raise MemoryReadError("Memory not opened - call open() first")

        try:
            self.mem_file.seek(address)
            data = self.mem_file.read(size)
            if len(data) != size:
                raise MemoryReadError(f"Short read at {hex(address)}: got {len(data)}, expected {size}")
            return data
        except Exception as e:
            raise MemoryReadError(f"Failed to read memory at {hex(address)}: {e}")


class Scanner:
    """Memory scanner for reading hackmud terminal output

    Usage:
        # Context manager (recommended)
        with Scanner() as scanner:
            text = scanner.read_window('shell', lines=30)

        # Manual
        scanner = Scanner()
        scanner.connect()
        text = scanner.read_window('shell')
        scanner.close()

    Args:
        config_dir: Directory containing scanner_config.json (defaults to script_dir/data/)
        memory_reader: Custom memory reader for testing (defaults to ProcMemReader)
    """

    @staticmethod
    def _get_caller_script_dir() -> Path:
        """Get the directory of the script that's using the Scanner API

        Returns the directory containing the main script that imported and
        is using the Scanner. Falls back to current working directory if
        running in interactive mode.
        """
        if hasattr(sys.modules['__main__'], '__file__'):
            main_file = sys.modules['__main__'].__file__
            if main_file:
                return Path(main_file).resolve().parent
        # Fallback to cwd if running in interactive mode (REPL, Jupyter, etc.)
        return Path.cwd()

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        memory_reader: Optional[MemoryReader] = None
    ):
        # Set config directory
        if config_dir is None:
            # Default to data/ in the same folder as the calling script
            config_dir = self._get_caller_script_dir() / 'data'
        self.config_dir = Path(config_dir)

        # Set memory reader (allows mocking for tests)
        self.memory_reader = memory_reader if memory_reader else ProcMemReader()

        # Debug flag (instance-level, overrides global)
        self._debug = _DEBUG

        # State
        self.connected = False
        self.pid: Optional[int] = None
        self.offsets: Optional[Dict] = None
        self.names: Optional[Dict] = None
        self.names_fixed: Optional[Dict] = None
        self.constants: Optional[Dict] = None

        # Cache for addresses (PID-specific)
        self._window_vtable: Optional[int] = None
        self._windows_cache: Dict = {}

    def __enter__(self):
        """Context manager entry - connects to game"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes connection"""
        self.close()
        return False

    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug output for this scanner instance

        Args:
            enabled: True to enable debug output, False to disable
        """
        self._debug = enabled
        if enabled:
            print('[DEBUG scanner] Debug mode enabled for this scanner instance')

    def _debug_print(self, *args, **kwargs):
        """Print debug message if debug is enabled"""
        if self._debug:
            print('[DEBUG scanner]', *args, **kwargs)

    def connect(self) -> None:
        """Connect to hackmud process and load configuration

        Raises:
            GameNotFoundError: If hackmud process is not running
            ConfigError: If configuration files are missing or invalid
        """
        if self.connected:
            return

        self._debug_print("Connecting to hackmud process...")

        # Find game process
        self.pid = config.get_game_pid()
        if self.pid is None:
            raise GameNotFoundError(
                "hackmud process not found. Make sure the game is running."
            )
        self._debug_print(f"  Found hackmud process: PID {self.pid}")

        # Load configuration files
        self._debug_print("  Loading configuration files...")
        self._load_config()

        # Open memory access
        self._debug_print(f"  Opening memory access for PID {self.pid}")
        self.memory_reader.open(self.pid)
        self.connected = True

        # Initialize vtable scanning
        self.init()

    def init(self) -> None:
        """Initialize scanner by finding vtables and scanning for windows

        This performs the expensive vtable and window scanning (~5s).
        Called automatically by connect().

        Uses address caching to speed up subsequent scans:
        - First run: Scan heap → find addresses → cache them (~5s)
        - Subsequent runs: Load cached addresses (~1ms)
        - Game restart: Detect PID change → rescan → update cache
        """
        if not self.connected:
            raise MemoryReadError("Not connected - call connect() first")

        # Try to load cached addresses first
        if self._load_addresses():
            self._debug_print("  Loaded addresses from cache (fast path)")
            return

        # Cache miss or invalid - do full scan
        self._debug_print("  Cache miss - scanning for windows (slow path)")
        self._scan_windows()

        # Save addresses for next time
        self._save_addresses()

    def close(self) -> None:
        """Close connection to game process"""
        if self.connected:
            self.memory_reader.close()
            self.connected = False

    def read_window(
        self,
        window_name: str,
        lines: int = 20,
        preserve_colors: bool = False
    ) -> List[str]:
        """Read text from a game window

        Args:
            window_name: Window to read ('shell', 'chat', 'badge', etc.)
            lines: Number of lines to return (default 20)
            preserve_colors: Keep Unity color tags (default False)

        Returns:
            List of text lines from the window

        Raises:
            WindowNotFoundError: If window is not found in memory
            MemoryReadError: If memory reading fails
        """
        if not self.connected:
            raise MemoryReadError("Not connected - call connect() first")

        # Validate window name
        if window_name not in self.constants['window_names']:
            valid_windows = ', '.join(self.constants['window_names'])
            raise ValueError(
                f"Invalid window name '{window_name}'. "
                f"Valid windows: {valid_windows}"
            )

        # Find window instance
        window_addr = self._find_window(window_name)
        if window_addr is None:
            raise WindowNotFoundError(
                f"Window '{window_name}' not found in memory. "
                f"Make sure the window is open in the game."
            )

        # Read text from window
        text = self._read_window_text(window_addr)

        # Process text
        if not preserve_colors:
            text = self._strip_colors(text)

        # Split into lines and return requested number
        all_lines = text.split('\n')
        return all_lines[-lines:] if lines > 0 else all_lines

    def get_version(self) -> str:
        """Read game version from memory or cache

        First checks if version is cached in constants.json. If not cached,
        scans memory for version string and caches it for future calls.

        This provides instant version lookup after the first call (~0.5ms vs ~550ms).
        Cache is automatically cleared when game updates are detected.

        Uses flexible regex pattern to match any version format (v1.x, v2.x, v3.x, etc.)

        Unity Scene Hierarchy: Scene → Main → Canvas → version → Text → m_Text

        Returns:
            Version string (e.g., "v2.016")

        Raises:
            MemoryReadError: If memory reading fails or version not found
        """
        if not self.connected:
            raise MemoryReadError("Not connected - call connect() first")

        # Check cache first
        if hasattr(self, 'constants') and self.constants.get('version'):
            return self.constants['version']

        # Not cached - scan memory (expensive operation)
        version = self._scan_memory_for_version()

        # Cache the version
        if hasattr(self, 'constants'):
            self.constants['version'] = version
            constants_file = self.config_dir / 'constants.json'
            try:
                with open(constants_file, 'w') as f:
                    json.dump(self.constants, f, indent=2)
            except Exception as e:
                # Non-fatal - just won't be cached for next run
                if self._debug:
                    print(f"[DEBUG scanner] Failed to cache version: {e}")

        return version

    def _scan_memory_for_version(self) -> str:
        """Scan memory for version string

        Internal method that performs the actual memory scanning.
        Called by get_version() when version is not cached.

        Returns:
            Version string (e.g., "v2.016")

        Raises:
            MemoryReadError: If version not found
        """
        # Search for version pattern "v#.###" in UTF-16 LE using flexible regex
        # Prioritize 3-digit minor versions (v2.016) over 2-digit (v2.16)
        # Avoid module versions like ":::what.next v2.4"
        import re

        try:
            regions = self._get_memory_regions()

            # Collect all candidate versions
            candidates = []

            for start, end in regions:
                size = end - start
                if size > 100 * 1024 * 1024:  # Skip huge regions
                    continue

                try:
                    data = self.memory_reader.read(start, size)

                    # Search for "v" prefix in UTF-16 LE (flexible pattern)
                    # Matches any version: v1.x, v2.x, v3.x, etc.
                    version_prefix = b'v\x00'
                    pos = 0

                    while True:
                        pos = data.find(version_prefix, pos)
                        if pos == -1:
                            break

                        # Extract version string
                        version_start = pos
                        version_end = min(pos + 64, len(data))
                        version_bytes = data[version_start:version_end]

                        try:
                            decoded = version_bytes.decode('utf-16le', errors='ignore')

                            # Extract version with regex - flexible pattern
                            # Matches: v1.2, v2.016, v3.100, etc.
                            match = re.match(r'v(\d+)\.(\d+)', decoded)
                            if match:
                                version_str = match.group(0)
                                minor = match.group(2)

                                # Get context to filter out module versions
                                context_start = max(0, pos - 64)
                                context_end = min(len(data), pos + 64)
                                context = data[context_start:context_end].decode('utf-16le', errors='ignore')

                                # Skip if this is a module version (contains ":::")
                                if ':::' in context:
                                    pos += 1
                                    continue

                                # Prefer longer minor versions (v2.016 over v2.16)
                                # and versions with 2+ digits (game versions over module versions)
                                if len(minor) >= 2:
                                    candidates.append((len(minor), version_str))

                        except UnicodeDecodeError:
                            pass

                        pos += 1

                        if len(candidates) >= 50:  # Collect up to 50 candidates
                            break

                except MemoryReadError:
                    continue

                if len(candidates) >= 50:
                    break

            # Return the version with longest minor number (most specific)
            if candidates:
                candidates.sort(reverse=True)  # Sort by minor length descending
                return candidates[0][1]

            # If we get here, version string was not found
            raise MemoryReadError(
                "Version string not found in memory. Make sure hackmud is fully loaded."
            )

        except Exception as e:
            raise MemoryReadError(f"Failed to read version: {e}")

    def _load_config(self) -> None:
        """Load configuration files

        Auto-generates config files in data/ folder if they don't exist.

        Raises:
            ConfigError: If config files are missing or invalid
        """
        # Check if config files exist, if not - auto-generate them
        offsets_file = self.config_dir / 'mono_offsets.json'
        config_file = self.config_dir / 'scanner_config.json'
        names_file = self.config_dir / 'mono_names_fixed.json'
        constants_file = self.config_dir / 'constants.json'

        files_missing = (
            not offsets_file.exists() or
            not config_file.exists() or
            not names_file.exists() or
            not constants_file.exists()
        )

        if files_missing:
            if self._debug:
                print(f"[DEBUG scanner] Config files missing in {self.config_dir}")
                print(f"[DEBUG scanner] Auto-generating config files...")

            try:
                config_generator.generate_configs(self.config_dir)
                if self._debug:
                    print(f"[DEBUG scanner] Config files generated successfully")
            except Exception as e:
                raise ConfigError(
                    f"Failed to auto-generate config files: {e}\n"
                    f"Make sure hackmud is installed and ilspycmd is available."
                )
        else:
            # Config files exist - check if they're up to date
            try:
                with open(config_file) as f:
                    config_data = json.load(f)

                stored_hash = config_data.get('checksum')
                game_path = Path(config_data.get('game_path', ''))

                if stored_hash and game_path.exists():
                    # Compute current hash
                    platform = config_data.get('platform', '')
                    core_dll = config_generator.get_core_dll_path(game_path, platform)
                    level0 = config_generator.get_level0_path(game_path, platform)

                    if core_dll.exists() and level0.exists():
                        current_hash = config_generator.compute_combined_hash(core_dll, level0)

                        if current_hash != stored_hash:
                            # Game updated - regenerate configs
                            if self._debug:
                                print(f"[DEBUG scanner] Game update detected (hash mismatch)")
                                print(f"[DEBUG scanner] Regenerating configs...")

                            try:
                                config_generator.generate_configs(self.config_dir, game_path)
                                if self._debug:
                                    print(f"[DEBUG scanner] Configs regenerated successfully")
                            except Exception as e:
                                print(f"Warning: Failed to regenerate configs: {e}")
                                print(f"Continuing with existing (potentially stale) configs...")
            except Exception as e:
                if self._debug:
                    print(f"[DEBUG scanner] Hash check failed: {e}")
                    print(f"[DEBUG scanner] Continuing with existing configs...")

        # Load mono_offsets.json
        if not offsets_file.exists():
            raise ConfigError(
                f"mono_offsets.json not found at {offsets_file} after generation. "
                f"This should not happen - please report as a bug."
            )

        try:
            with open(offsets_file) as f:
                data = json.load(f)

                # Flatten nested offset structure for easy access
                self.offsets = {}
                self.names = data.get('class_names', {})

                # Extract mono offsets (convert hex strings to int)
                for key, value in data.get('mono_offsets', {}).items():
                    self.offsets[key] = int(value, 16) if isinstance(value, str) else value

                # Extract window offsets
                for key, value in data.get('window_offsets', {}).items():
                    self.offsets[f'window_{key}'] = int(value, 16) if isinstance(value, str) else value

                # Extract TMP offsets
                for key, value in data.get('tmp_offsets', {}).items():
                    self.offsets[f'tmp_{key}'] = int(value, 16) if isinstance(value, str) else value

        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in mono_offsets.json: {e}")

        # Load mono_names_fixed.json
        names_fixed_file = self.config_dir / 'mono_names_fixed.json'
        if not names_fixed_file.exists():
            raise ConfigError(f"mono_names_fixed.json not found at {names_fixed_file}")

        try:
            with open(names_fixed_file) as f:
                self.names_fixed = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in mono_names_fixed.json: {e}")

        # Load constants.json (window names extracted during update_offsets.py)
        constants_file = self.config_dir / 'constants.json'
        if not constants_file.exists():
            raise ConfigError(
                f"constants.json not found at {constants_file}. "
                f"Run update_offsets.py to generate it."
            )

        try:
            with open(constants_file) as f:
                self.constants = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in constants.json: {e}")

    def _load_addresses(self) -> bool:
        """Load cached window addresses from mono_addresses.json

        Returns:
            True if addresses loaded successfully and are valid for current PID
            False if cache miss, PID mismatch, or validation failed
        """
        addresses_file = self.config_dir / 'mono_addresses.json'
        if not addresses_file.exists():
            self._debug_print("    No address cache file found")
            return False

        try:
            with open(addresses_file) as f:
                cache = json.load(f)

            # Check PID - addresses are invalid if game restarted
            cached_pid = cache.get('pid')
            if cached_pid != self.pid:
                self._debug_print(f"    PID mismatch: cached={cached_pid}, current={self.pid}")
                return False

            # Load window vtable
            vtable_hex = cache.get('vtables', {}).get('Window')
            if not vtable_hex:
                self._debug_print("    No Window vtable in cache")
                return False
            self._window_vtable = int(vtable_hex, 16)

            # Load window addresses
            windows = cache.get('windows', {})
            if not windows:
                self._debug_print("    No window addresses in cache")
                return False

            # Validate cached addresses by trying to read from them
            self._windows_cache = {}
            for window_name, data in windows.items():
                window_addr = int(data['window_addr'], 16)
                tmp_addr = int(data['tmp_addr'], 16)

                # Validate by reading window name
                try:
                    name_offset = self.offsets.get('window_name', 0x90)
                    name_ptr = self._read_pointer(window_addr + name_offset)
                    if name_ptr and name_ptr != 0:
                        name = self._read_mono_string(name_ptr)
                        if name == window_name:
                            self._windows_cache[window_name] = (window_addr, tmp_addr)
                        else:
                            # Name doesn't match - cache is stale
                            self._debug_print(f"    Window name mismatch: expected={window_name}, got={name}")
                            self._windows_cache = {}
                            return False
                except (MemoryReadError, struct.error) as e:
                    # Read failed - cache is invalid
                    self._debug_print(f"    Failed to validate {window_name}: {e}")
                    self._windows_cache = {}
                    return False

            # All addresses validated successfully
            self._debug_print(f"    Loaded {len(self._windows_cache)} windows from cache")
            return True

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self._debug_print(f"    Failed to load address cache: {e}")
            return False

    def _save_addresses(self) -> None:
        """Save window addresses to mono_addresses.json for faster subsequent scans

        Saves:
        - Current PID (for invalidation detection)
        - Window vtable address
        - Window instance addresses (window_addr, tmp_addr) for each window
        """
        if not hasattr(self, '_windows_cache') or not self._windows_cache:
            self._debug_print("    No windows to cache")
            return

        addresses_file = self.config_dir / 'mono_addresses.json'

        cache = {
            'pid': self.pid,
            'vtables': {},
            'windows': {}
        }

        # Save window vtable
        if self._window_vtable:
            cache['vtables']['Window'] = hex(self._window_vtable)

        # Save window addresses
        for window_name, (window_addr, tmp_addr) in self._windows_cache.items():
            cache['windows'][window_name] = {
                'window_addr': hex(window_addr),
                'tmp_addr': hex(tmp_addr)
            }

        try:
            with open(addresses_file, 'w') as f:
                json.dump(cache, f, indent=2)
            self._debug_print(f"    Saved {len(self._windows_cache)} windows to cache")
        except Exception as e:
            # Non-fatal - caching is optional
            if self._debug:
                print(f"[DEBUG scanner] Failed to save address cache: {e}")

    def _find_window(self, window_name: str) -> Optional[int]:
        """Find Window instance in memory by name

        Args:
            window_name: Name of window to find

        Returns:
            Memory address of Window instance, or None if not found
        """
        # Return window address from cache (populated by init())
        if not hasattr(self, '_windows_cache'):
            raise MemoryReadError("Scanner not initialized - call init() first")

        window_data = self._windows_cache.get(window_name)
        if window_data:
            return window_data[0]  # Return window_addr
        return None

    def _scan_windows(self) -> None:
        """Scan memory for all Window instances and cache them

        Populates _windows_cache with {name: (window_addr, tmp_addr)}
        """
        self._windows_cache = {}

        # Find Window class vtable
        window_vtable = self._find_window_vtable()
        if not window_vtable:
            return

        # Cache vtable for saving later
        self._window_vtable = window_vtable

        # Scan memory regions for Window instances
        window_vtable_bytes = struct.pack('<Q', window_vtable)
        regions = self._get_memory_regions()

        for start, end in regions:
            try:
                data = self.memory_reader.read(start, end - start)
            except MemoryReadError:
                continue

            # Search for vtable pointer in this region
            pos = 0
            while True:
                pos = data.find(window_vtable_bytes, pos)
                if pos == -1:
                    break

                window_addr = start + pos

                # Read window name
                name_offset = self.offsets.get('window_name', 0x90)
                try:
                    name_ptr = self._read_pointer(window_addr + name_offset)
                    if name_ptr and name_ptr != 0:
                        name = self._read_mono_string(name_ptr)

                        # If name matches one of the known windows, cache it
                        if name in self.constants['window_names']:
                            # Get TMP instance via gui_text pointer
                            gui_text_offset = self.offsets.get('window_gui_text', 0x58)
                            tmp_ptr = self._read_pointer(window_addr + gui_text_offset)

                            if tmp_ptr and tmp_ptr != 0:
                                self._windows_cache[name] = (window_addr, tmp_ptr)
                except (MemoryReadError, struct.error):
                    pass

                pos += 8

    def _find_window_vtable(self) -> Optional[int]:
        """Find hackmud.Window class vtable

        Returns:
            Vtable address, or None if not found
        """
        heap = self._get_heap_region()
        if not heap:
            return None

        start, end = heap
        try:
            data = self.memory_reader.read(start, end - start)
        except MemoryReadError:
            return None

        # MonoClass offsets
        name_offset = self.offsets.get('mono_class_name', 0x40)
        namespace_offset = self.offsets.get('mono_class_namespace', 0x48)
        runtime_info_offset = self.offsets.get('mono_class_runtime_info', 0xC8)
        vtable_offset = self.offsets.get('mono_runtime_info_vtable', 0x8)

        # Get target class and namespace names
        window_class = self.names_fixed.get('window_class', 'Window')
        window_namespace = self.names_fixed.get('window_namespace', 'hackmud')

        # Scan heap for MonoClass
        for offset in range(0, len(data) - 0x100, 8):
            try:
                # Read class name pointer
                name_ptr_bytes = data[offset + name_offset:offset + name_offset + 8]
                if len(name_ptr_bytes) < 8:
                    continue
                name_ptr = struct.unpack('<Q', name_ptr_bytes)[0]

                if not self._is_valid_pointer(name_ptr):
                    continue

                # Read class name
                name = self._read_cstring(name_ptr, 32)
                if name != window_class:
                    continue

                # Read namespace pointer
                ns_ptr_bytes = data[offset + namespace_offset:offset + namespace_offset + 8]
                if len(ns_ptr_bytes) < 8:
                    continue
                ns_ptr = struct.unpack('<Q', ns_ptr_bytes)[0]

                if not self._is_valid_pointer(ns_ptr):
                    continue

                # Read namespace
                namespace = self._read_cstring(ns_ptr, 64)
                if namespace != window_namespace:
                    continue

                # Found the class! Get vtable from runtime_info
                runtime_info_bytes = data[offset + runtime_info_offset:offset + runtime_info_offset + 8]
                if len(runtime_info_bytes) < 8:
                    continue
                runtime_info = struct.unpack('<Q', runtime_info_bytes)[0]

                if runtime_info and self._is_valid_pointer(runtime_info):
                    vtable = self._read_pointer(runtime_info + vtable_offset)
                    if vtable:
                        return vtable

            except (struct.error, MemoryReadError):
                continue

        return None

    def _get_memory_regions(self) -> List[Tuple[int, int]]:
        """Get readable/writable memory regions from /proc/PID/maps

        Returns:
            List of (start, end) address tuples
        """
        regions = []
        try:
            with open(f'/proc/{self.pid}/maps') as f:
                for line in f:
                    if 'rw-p' in line:
                        addrs = line.split()[0].split('-')
                        start = int(addrs[0], 16)
                        end = int(addrs[1], 16)
                        # Skip huge regions (> 100MB)
                        if end - start < 100 * 1024 * 1024:
                            regions.append((start, end))
        except (FileNotFoundError, PermissionError):
            pass
        return regions

    def _get_heap_region(self) -> Optional[Tuple[int, int]]:
        """Get heap memory region from /proc/PID/maps

        Returns:
            (start, end) tuple or None
        """
        try:
            with open(f'/proc/{self.pid}/maps') as f:
                for line in f:
                    if '[heap]' in line:
                        addrs = line.split()[0].split('-')
                        return (int(addrs[0], 16), int(addrs[1], 16))
        except (FileNotFoundError, PermissionError):
            pass
        return None

    def _read_cstring(self, address: int, max_len: int = 256) -> Optional[str]:
        """Read null-terminated C string from memory

        Args:
            address: Memory address to read from
            max_len: Maximum length to read

        Returns:
            String content or None if read fails
        """
        try:
            data = self.memory_reader.read(address, max_len)
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8', errors='ignore')
        except (MemoryReadError, ValueError, UnicodeDecodeError):
            return None

    def _is_valid_pointer(self, ptr: int) -> bool:
        """Check if pointer looks valid

        Args:
            ptr: Pointer value to check

        Returns:
            True if pointer is in valid range
        """
        return 0x1000 < ptr < 0x7FFFFFFFFFFF

    def _load_cached_vtable(self) -> Optional[int]:
        """Load cached Window vtable address from config

        Returns:
            Cached vtable address or None
        """
        try:
            config_file = self.config_dir / 'scanner_config.json'
            if not config_file.exists():
                return None

            with open(config_file) as f:
                data = json.load(f)
                vtable_hex = data.get('window_vtable')
                if vtable_hex:
                    return int(vtable_hex, 16)
        except:
            pass
        return None

    def _save_vtable_cache(self, vtable: int) -> None:
        """Save Window vtable address to config for faster subsequent scans

        Args:
            vtable: Vtable address to cache
        """
        try:
            config_file = self.config_dir / 'scanner_config.json'

            # Load existing config
            data = {}
            if config_file.exists():
                with open(config_file) as f:
                    data = json.load(f)

            # Update with vtable
            data['window_vtable'] = hex(vtable)

            # Save back
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass  # Cache is optional, don't fail if we can't save

    def _read_window_text(self, window_addr: int) -> str:
        """Read text content from Window instance

        Args:
            window_addr: Memory address of Window object

        Returns:
            Text content from window
        """
        # Get gui_text pointer (Window.gui_text)
        gui_text_offset = self.offsets.get('window_gui_text', 0x58)
        gui_text_ptr = self._read_pointer(window_addr + gui_text_offset)

        if gui_text_ptr == 0:
            raise MemoryReadError("Window.gui_text is null")

        # Read m_text field pointer (TMP_Text.m_text is a MonoString*)
        m_text_offset = self.offsets.get('tmp_m_text', 0xc8)
        m_text_ptr = self._read_pointer(gui_text_ptr + m_text_offset)

        if m_text_ptr == 0:
            return ""

        # Read the MonoString
        text = self._read_mono_string(m_text_ptr)

        return text

    def _read_pointer(self, address: int) -> int:
        """Read 64-bit pointer from memory

        Args:
            address: Memory address to read from

        Returns:
            Pointer value
        """
        data = self.memory_reader.read(address, 8)
        return struct.unpack('<Q', data)[0]

    def _read_mono_string(self, string_ptr: int) -> str:
        """Read MonoString from memory

        Args:
            string_ptr: Pointer to MonoString object (not a pointer to a pointer)

        Returns:
            String content
        """
        if not string_ptr or string_ptr == 0:
            return ""

        # Get MonoString field offsets
        length_offset = self.offsets.get('mono_string_length', 0x10)
        data_offset = self.offsets.get('mono_string_data', 0x14)

        # Read length (int32)
        try:
            length_data = self.memory_reader.read(string_ptr + length_offset, 4)
            length = struct.unpack('<i', length_data)[0]
        except:
            return ""

        if length <= 0 or length > 1000000:  # Sanity check
            return ""

        # Read UTF-16 string data
        try:
            string_data = self.memory_reader.read(string_ptr + data_offset, length * 2)
            return string_data.decode('utf-16le', errors='ignore')
        except:
            return ""

    def _read_mono_string_at(self, obj_addr: int, offset: int) -> str:
        """Read MonoString from an object field

        Args:
            obj_addr: Address of the object
            offset: Offset to the string pointer field

        Returns:
            String content
        """
        try:
            # Read pointer to MonoString
            ptr_data = self.memory_reader.read(obj_addr + offset, 8)
            string_ptr = struct.unpack('<Q', ptr_data)[0]
            return self._read_mono_string(string_ptr)
        except:
            return ""

    def _find_mono_class(self, class_name: str, namespace: str) -> Optional[int]:
        """Find MonoClass in Mono runtime

        Args:
            class_name: Class name to find
            namespace: Namespace of the class

        Returns:
            Address of MonoClass, or None if not found
        """
        # This is a simplified implementation
        # In practice, we'd need to walk the Mono assembly structures
        # For now, return None and rely on version window fallback
        return None

    def _get_class_vtable(self, class_addr: int) -> Optional[int]:
        """Get vtable address from MonoClass

        Args:
            class_addr: Address of MonoClass

        Returns:
            Vtable address, or None if failed
        """
        try:
            # Read runtime_info (+0xC8)
            runtime_info_data = self.memory_reader.read(class_addr + 0xC8, 8)
            runtime_info = struct.unpack('<Q', runtime_info_data)[0]

            if runtime_info == 0:
                return None

            # Read vtable (+0x8 from runtime_info)
            vtable_data = self.memory_reader.read(runtime_info + 0x8, 8)
            vtable = struct.unpack('<Q', vtable_data)[0]

            return vtable if vtable != 0 else None
        except:
            return None

    def _strip_colors(self, text: str) -> str:
        """Strip Unity color tags from text

        Args:
            text: Text with color tags

        Returns:
            Text without color tags
        """
        import re
        # Remove <color=...> and </color> tags
        text = re.sub(r'<color=[^>]+>', '', text)
        text = re.sub(r'</color>', '', text)
        return text

"""Configuration management for hackmud memory scanner

Handles platform-specific paths, auto-detection, and config file creation.
"""

import json
import hashlib
import platform
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


# Debug flag from environment
DEBUG = os.getenv('HACKMUD_DEBUG', '').lower() in ('1', 'true', 'yes')

def _debug_print(*args, **kwargs):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print('[DEBUG config]', *args, **kwargs)


# Default installation paths by platform
DEFAULT_GAME_PATHS = {
    'Linux': Path.home() / ".local/share/Steam/steamapps/common/hackmud",
    'Windows': Path("C:/Program Files (x86)/Steam/steamapps/common/hackmud"),
    'Darwin': Path.home() / "Library/Application Support/Steam/steamapps/common/hackmud"
}

DEFAULT_SETTINGS_PATHS = {
    'Linux': Path.home() / ".config/unity3d/Drizzly Bear/hackmud",
    'Windows': Path.home() / "AppData/LocalLow/Drizzly Bear/hackmud",
    'Darwin': Path.home() / "Library/Application Support/Drizzly Bear/hackmud"
}


def get_platform() -> str:
    """Get current platform name"""
    return platform.system()


def get_core_dll_path(game_path: Path, plat: str) -> Path:
    """Generate Core.dll path from game base path and platform

    Args:
        game_path: Base hackmud installation directory
        plat: Platform name (Linux, Windows, Darwin)

    Returns:
        Path to Core.dll

    Raises:
        ValueError: If platform is unsupported
    """
    if plat == 'Linux':
        return game_path / "hackmud_lin_Data/Managed/Core.dll"
    elif plat == 'Windows':
        return game_path / "hackmud_Data/Managed/Core.dll"
    elif plat == 'Darwin':
        return game_path / "hackmud.app/Contents/Resources/Data/Managed/Core.dll"
    else:
        raise ValueError(f"Unsupported platform: {plat}")


def detect_game_path(plat: Optional[str] = None) -> Optional[Path]:
    """Try to auto-detect game installation path

    Args:
        plat: Platform name (defaults to current platform)

    Returns:
        Path to game installation, or None if not found
    """
    if plat is None:
        plat = get_platform()

    # Try default location first
    default_path = DEFAULT_GAME_PATHS.get(plat)
    if default_path and default_path.exists():
        core_dll = get_core_dll_path(default_path, plat)
        if core_dll.exists():
            return default_path

    # Try alternative Steam locations
    if plat == 'Linux':
        search_paths = [
            Path.home() / ".local/share/Steam/steamapps/common/hackmud",
            Path.home() / ".steam/steam/steamapps/common/hackmud",
        ]
    elif plat == 'Windows':
        search_paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/hackmud"),
            Path("C:/Program Files/Steam/steamapps/common/hackmud"),
        ]
    else:
        search_paths = []

    for path in search_paths:
        if path.exists():
            core_dll = get_core_dll_path(path, plat)
            if core_dll.exists():
                return path

    return None


def detect_settings_path(plat: Optional[str] = None) -> Optional[Path]:
    """Try to auto-detect settings path

    Args:
        plat: Platform name (defaults to current platform)

    Returns:
        Path to settings directory, or None if not found
    """
    if plat is None:
        plat = get_platform()

    default_path = DEFAULT_SETTINGS_PATHS.get(plat)
    if default_path and default_path.exists():
        return default_path

    return None


def compute_dll_hash(dll_path: Path) -> str:
    """Compute SHA256 hash of Core.dll

    Args:
        dll_path: Path to Core.dll

    Returns:
        Hexadecimal SHA256 hash string
    """
    sha256 = hashlib.sha256()
    with open(dll_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_combined_hash(core_dll: Path, level0: Path) -> str:
    """Compute combined SHA256 hash of Core.dll and level0 files

    This creates a single hash that detects changes to either file,
    ensuring both class names and window names are regenerated together.

    Args:
        core_dll: Path to Core.dll
        level0: Path to level0 Unity scene file

    Returns:
        Hexadecimal SHA256 hash string of both files combined
    """
    _debug_print(f"Computing combined hash for:")
    _debug_print(f"  Core.dll: {core_dll}")
    _debug_print(f"  level0: {level0}")

    sha256 = hashlib.sha256()

    # Hash Core.dll
    core_dll_size = 0
    with open(core_dll, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            core_dll_size += len(chunk)
            sha256.update(chunk)
    _debug_print(f"  Core.dll size: {core_dll_size:,} bytes")

    # Hash level0
    level0_size = 0
    with open(level0, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            level0_size += len(chunk)
            sha256.update(chunk)
    _debug_print(f"  level0 size: {level0_size:,} bytes")

    result = sha256.hexdigest()
    _debug_print(f"  Combined hash: {result[:16]}...")
    return result


def get_game_pid(plat: Optional[str] = None) -> Optional[int]:
    """Get hackmud process ID

    Args:
        plat: Platform name (defaults to current platform)

    Returns:
        Process ID if found, None otherwise
    """
    if plat is None:
        plat = get_platform()

    try:
        if plat == 'Linux' or plat == 'Darwin':
            # Use pgrep to find hackmud process (matches substring)
            result = subprocess.run(
                ['pgrep', 'hackmud'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        elif plat == 'Windows':
            # Use tasklist to find hackmud.exe
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq hackmud.exe', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and 'hackmud.exe' in result.stdout:
                # Parse CSV output: "hackmud.exe","PID",...
                parts = result.stdout.split(',')
                if len(parts) >= 2:
                    return int(parts[1].strip('"'))
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass

    return None


def create_config(
    game_path: Optional[Path] = None,
    settings_path: Optional[Path] = None,
    plat: Optional[str] = None
) -> Dict[str, str]:
    """Create configuration dictionary

    Args:
        game_path: Path to game installation (auto-detects if None)
        settings_path: Path to settings directory (auto-detects if None)
        plat: Platform name (defaults to current platform)

    Returns:
        Configuration dictionary

    Raises:
        ValueError: If game path cannot be found
    """
    if plat is None:
        plat = get_platform()

    # Auto-detect game path if not provided
    if game_path is None:
        game_path = detect_game_path(plat)
        if game_path is None:
            raise ValueError(
                "Could not detect game installation path. "
                "Please provide game_path argument."
            )

    # Auto-detect settings path if not provided
    if settings_path is None:
        settings_path = detect_settings_path(plat)

    # Get Core.dll and level0 paths
    core_dll = get_core_dll_path(game_path, plat)
    if not core_dll.exists():
        raise ValueError(f"Core.dll not found at {core_dll}")

    level0 = get_level0_path(game_path, plat)

    # Compute combined hash of both files
    checksum = compute_combined_hash(core_dll, level0)

    # Get game PID if running
    game_pid = get_game_pid(plat)

    # Build config
    config = {
        'platform': plat,
        'game_path': str(game_path),
        'checksum': checksum,
        'date_last': datetime.now().isoformat()
    }

    if settings_path:
        config['settings_path'] = str(settings_path)

    if game_pid is not None:
        config['game_pid'] = game_pid

    return config


def save_config(config: Dict[str, str], config_file: Path) -> None:
    """Save configuration to JSON file

    Args:
        config: Configuration dictionary
        config_file: Path to save config.json
    """
    # Update date_last on every save
    config['date_last'] = datetime.now().isoformat()

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def load_config(config_file: Path) -> Dict[str, str]:
    """Load configuration from JSON file

    Args:
        config_file: Path to config.json

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid
    """
    with open(config_file, 'r') as f:
        return json.load(f)


def get_level0_path(game_path: Path, plat: Optional[str] = None) -> Path:
    """Get path to Unity level0 scene file

    Args:
        game_path: Path to game installation
        plat: Platform name (defaults to current platform)

    Returns:
        Path to level0 file

    Raises:
        ValueError: If platform is unsupported
        FileNotFoundError: If level0 file doesn't exist
    """
    if plat is None:
        plat = get_platform()

    if plat == 'Linux':
        level0_path = game_path / "hackmud_lin_Data/level0"
    elif plat == 'Windows':
        level0_path = game_path / "hackmud_Data/level0"
    elif plat == 'Darwin':
        level0_path = game_path / "hackmud.app/Contents/Resources/Data/level0"
    else:
        raise ValueError(f"Unsupported platform: {plat}")

    if not level0_path.exists():
        raise FileNotFoundError(f"level0 not found at {level0_path}")

    return level0_path


def extract_window_names(level0_path: Path) -> list:
    """Extract window names from Unity level0 scene file

    Args:
        level0_path: Path to level0 file

    Returns:
        Sorted list of window names found in level0

    Raises:
        ImportError: If UnityPy is not installed
        Exception: If level0 parsing fails
    """
    try:
        import UnityPy
    except ImportError:
        raise ImportError(
            "UnityPy is required to extract window names. "
            "Install with: pip install UnityPy"
        )

    # Load and parse level0
    env = UnityPy.load(str(level0_path))

    # Extract window names
    window_names = set()
    known_windows = ['shell', 'chat', 'badge', 'breach', 'scratch', 'binlog', 'binmat', 'version']

    for obj in env.objects:
        if obj.type.name == "GameObject":
            data = obj.read()
            name = data.m_Name
            # Check if this is a known window
            if name.lower() in known_windows:
                window_names.add(name)

    return sorted(window_names)

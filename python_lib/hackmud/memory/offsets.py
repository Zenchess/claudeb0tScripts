"""Offset generation and management for hackmud memory scanner

Handles Core.dll decompilation and offset extraction.
"""

import subprocess
import re
import json
import shutil
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

# Import config module for hash computation
try:
    from . import config
except ImportError:
    # Fallback for direct execution
    import config


# Debug flag from environment
DEBUG = os.getenv('HACKMUD_DEBUG', '').lower() in ('1', 'true', 'yes')

def _debug_print(*args, **kwargs):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print('[DEBUG offsets]', *args, **kwargs)


# Default decompilation output directory
DEFAULT_OUTPUT_DIR = Path("/tmp/hackmud_decompiled")


def decompile_dll(core_dll: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    """Decompile Core.dll using ilspycmd

    Args:
        core_dll: Path to Core.dll
        output_dir: Output directory (defaults to /tmp/hackmud_decompiled)

    Returns:
        Path to decompiled .cs file, or None if failed
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # Clean and recreate output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "Core.decompiled.cs"

    print(f"Decompiling {core_dll}...")

    # Find ilspycmd (check ~/.dotnet/tools first, then PATH)
    ilspycmd = Path.home() / ".dotnet/tools/ilspycmd"
    if not ilspycmd.exists():
        ilspycmd = "ilspycmd"  # Try PATH

    result = subprocess.run(
        [str(ilspycmd), str(core_dll), "-o", str(output_file)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    # ilspycmd creates a directory with the same name, containing the .cs file
    actual_file = output_file / "Core.decompiled.cs"
    if actual_file.exists():
        print(f"Decompiled to {actual_file}")
        return actual_file
    elif output_file.is_file():
        print(f"Decompiled to {output_file}")
        return output_file
    else:
        print(f"Error: Could not find decompiled file")
        return None


def find_window_class(code: str) -> Dict[str, str]:
    """Find the Window class and its output field type

    Args:
        code: Decompiled C# source code

    Returns:
        Dictionary with window_class, window_namespace, and output_class
    """
    offsets = {}

    # Look for hackmud.Window class specifically
    # Pattern: namespace hackmud { ... public class Window : MonoBehaviour ... }
    window_match = re.search(
        r'namespace hackmud\s*\{[^}]*?public class Window\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
        code, re.DOTALL
    )

    if window_match:
        offsets['window_class'] = 'Window'
        offsets['window_namespace'] = 'hackmud'
        offsets['output_class'] = window_match.group(1)
        print(f"Found Window class: hackmud.Window")
        print(f"Found output type: {offsets['output_class']}")
    else:
        # Alternative: Find any class with gui_text field
        gui_text_match = re.search(
            r'public class (\w+)\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
            code, re.DOTALL
        )
        if gui_text_match:
            offsets['window_class'] = gui_text_match.group(1)
            offsets['output_class'] = gui_text_match.group(2)
            print(f"Found Window class: {offsets['window_class']}")
            print(f"Found output type: {offsets['output_class']}")

    return offsets


def find_queue_class(code: str, output_class: str) -> Dict[str, str]:
    """Find the Queue<string> field in the output class

    Args:
        code: Decompiled C# source code
        output_class: Name of the output class to search in

    Returns:
        Dictionary with queue_field
    """
    offsets = {}

    # Find the output class definition
    pattern = rf'public class {output_class}\s*\{{.*?public Queue<string> (\w+)\s*='
    match = re.search(pattern, code, re.DOTALL)

    if match:
        offsets['queue_field'] = match.group(1)
        print(f"Found Queue<string> field: {offsets['queue_field']}")

    return offsets


def generate_offsets(core_dll: Path, output_dir: Optional[Path] = None) -> Dict[str, any]:
    """Generate offset information from Core.dll

    Args:
        core_dll: Path to Core.dll
        output_dir: Output directory for decompilation (optional)

    Returns:
        Dictionary with class names and offset information

    Raises:
        RuntimeError: If decompilation fails or class names not found
    """
    # Decompile
    output_file = decompile_dll(core_dll, output_dir)
    if not output_file or not output_file.exists():
        raise RuntimeError("Decompilation failed")

    # Read decompiled code
    code = output_file.read_text()

    # Find class names
    class_info = {}
    class_info.update(find_window_class(code))

    if 'output_class' not in class_info:
        raise RuntimeError("Could not find Window class in decompiled code")

    class_info.update(find_queue_class(code, class_info['output_class']))

    if 'queue_field' not in class_info:
        raise RuntimeError("Could not find Queue<string> field in output class")

    return class_info


def save_names(class_info: Dict[str, str], names_file: Path) -> None:
    """Save obfuscated class names to mono_names.json

    Only saves obfuscated names that change each game update.
    Non-obfuscated names are in mono_names_fixed.json.

    Args:
        class_info: Dictionary with class names
        names_file: Path to mono_names.json
    """
    # Only save obfuscated names
    names = {
        'output_class': class_info.get('output_class'),
        'queue_field': class_info.get('queue_field')
    }

    # Save names
    with open(names_file, 'w') as f:
        json.dump(names, f, indent=2)

    print(f"Class names saved to {names_file}")


def load_names(names_file: Path) -> Dict:
    """Load class names from mono_names.json

    Args:
        names_file: Path to mono_names.json

    Returns:
        Class names dictionary

    Raises:
        FileNotFoundError: If names file doesn't exist
        json.JSONDecodeError: If names file is invalid
    """
    with open(names_file, 'r') as f:
        return json.load(f)


def load_offsets(offsets_file: Path) -> Dict:
    """Load numeric offsets from mono_offsets.json

    Args:
        offsets_file: Path to mono_offsets.json

    Returns:
        Offsets dictionary

    Raises:
        FileNotFoundError: If offsets file doesn't exist
        json.JSONDecodeError: If offsets file is invalid
    """
    with open(offsets_file, 'r') as f:
        return json.load(f)


def generate_constants(constants_file: Path) -> Dict:
    """Generate runtime constants

    DEPRECATED: Window names are now dynamically extracted from level0
    using config.extract_window_names(). This function is kept for
    backwards compatibility only and creates a fallback constants.json.

    Args:
        constants_file: Path to save constants.json

    Returns:
        Constants dictionary
    """
    # Default constants (can be enhanced to read from game memory later)
    constants = {
        "version": "v2.016",  # Default, could be read from game memory
        "window_names": [
            "shell",
            "chat",
            "badge",
            "breach",
            "scratch",
            "binlog",
            "binmat",
            "version"
        ]
    }

    # Save constants
    with open(constants_file, 'w') as f:
        json.dump(constants, f, indent=2)

    print(f"Constants saved to {constants_file}")
    return constants


def update_offsets(
    core_dll: Path,
    config_file: Path,
    names_file: Path,
    offsets_file: Optional[Path] = None,
    output_dir: Optional[Path] = None
) -> Tuple[Dict, bool]:
    """Update class names only if Core.dll hash has changed

    This function checks if the Core.dll hash in the config matches the
    current Core.dll file. If it matches, existing names are returned.
    If it doesn't match (or config doesn't exist), names are regenerated.

    Args:
        core_dll: Path to Core.dll
        config_file: Path to config.json
        names_file: Path to mono_names.json
        offsets_file: Path to mono_offsets.json (optional, for backward compatibility)
        output_dir: Output directory for decompilation (optional)

    Returns:
        Tuple of (names_dict, regenerated_bool) where:
        - names_dict: The class names dictionary
        - regenerated_bool: True if names were regenerated, False if cached

    Raises:
        RuntimeError: If regeneration is needed but fails
    """
    # Try to load existing config and names
    _debug_print("Checking if class names need regeneration...")
    _debug_print(f"  config_file: {config_file}")
    _debug_print(f"  names_file: {names_file}")
    _debug_print(f"  core_dll: {core_dll}")

    need_regen = False
    reason = ""

    if not config_file.exists():
        need_regen = True
        reason = "Config file doesn't exist"
        _debug_print(f"  → {reason}")
    elif not names_file.exists():
        need_regen = True
        reason = "Names file doesn't exist"
        _debug_print(f"  → {reason}")
    else:
        try:
            # Load config to get stored checksum and PID
            cfg = config.load_config(config_file)
            stored_checksum = cfg.get('checksum') or cfg.get('core_dll_hash')  # Backward compat
            stored_pid = cfg.get('game_pid')
            _debug_print(f"  stored checksum: {stored_checksum[:16] if stored_checksum else None}...")
            _debug_print(f"  stored PID: {stored_pid}")

            # PID optimization: if game PID matches, skip expensive hash check
            if stored_pid is not None:
                current_pid = config.get_game_pid()
                _debug_print(f"  current PID: {current_pid}")
                if current_pid == stored_pid:
                    # Game hasn't restarted - use cached names without hashing
                    _debug_print("  → PID matches, using cached names")
                    print(f"Game PID matches ({current_pid}) - using existing class names (hash check skipped)")
                    return load_names(names_file), False

            if not stored_checksum:
                need_regen = True
                reason = "No checksum in config"
                _debug_print(f"  → {reason}")
            else:
                # Compute current combined hash
                plat = cfg.get('platform', config.get_platform())
                game_path = Path(cfg['game_path'])
                level0 = config.get_level0_path(game_path, plat)
                _debug_print("  Computing current checksum...")
                current_checksum = config.compute_combined_hash(core_dll, level0)

                if stored_checksum != current_checksum:
                    need_regen = True
                    reason = f"Checksum mismatch (stored: {stored_checksum[:8]}..., current: {current_checksum[:8]}...)"
                    _debug_print(f"  → {reason}")
                else:
                    # Checksum matches - use existing names
                    _debug_print("  → Checksum matches, using cached names")
                    print(f"Game files checksum matches ({current_checksum[:8]}...) - using existing class names")
                    return load_names(names_file), False

        except Exception as e:
            need_regen = True
            reason = f"Error loading config/names: {e}"
            _debug_print(f"  → {reason}")

    # Need to regenerate
    if need_regen:
        print(f"Regenerating class names: {reason}")
        class_info = generate_offsets(core_dll, output_dir)
        save_names(class_info, names_file)

        # Return the regenerated names
        return load_names(names_file), True

    # Should never reach here, but just in case
    raise RuntimeError("Unexpected state in update_offsets")

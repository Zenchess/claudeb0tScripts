#!/usr/bin/env python3
"""
Config file generator for hackmud memory scanner.

Auto-generates mono_offsets.json, scanner_config.json, constants.json,
and mono_names_fixed.json when Scanner.connect() is called.
"""

import subprocess
import re
import json
import os
import hashlib
import platform
import shutil
from pathlib import Path
from typing import Optional, Dict, Tuple

# Debug flag from environment
DEBUG = os.getenv('HACKMUD_DEBUG', '').lower() in ('1', 'true', 'yes')

def _debug_print(*args, **kwargs):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print('[DEBUG config_generator]', *args, **kwargs)


# Default paths by platform
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


def get_core_dll_path(game_path: Path, plat: str) -> Path:
    """Generate Core.dll path from game base path and platform"""
    if plat == 'Linux':
        return game_path / "hackmud_lin_Data/Managed/Core.dll"
    elif plat == 'Windows':
        return game_path / "hackmud_Data/Managed/Core.dll"
    elif plat == 'Darwin':
        return game_path / "hackmud.app/Contents/Resources/Data/Managed/Core.dll"
    else:
        raise ValueError(f"Unsupported platform: {plat}")


def get_level0_path(game_path: Path, plat: str) -> Path:
    """Generate level0 path from game base path and platform"""
    if plat == 'Linux':
        return game_path / "hackmud_lin_Data/level0"
    elif plat == 'Windows':
        return game_path / "hackmud_Data/level0"
    elif plat == 'Darwin':
        return game_path / "hackmud.app/Contents/Resources/Data/level0"
    else:
        raise ValueError(f"Unsupported platform: {plat}")


def detect_game_path() -> Optional[Path]:
    """Try to detect game installation path"""
    plat = platform.system()
    default_path = DEFAULT_GAME_PATHS.get(plat)

    if default_path and default_path.exists():
        return default_path

    # Try to find via Core.dll
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


def compute_combined_hash(core_dll: Path, level0: Path) -> str:
    """Compute combined SHA256 hash of Core.dll and level0 files"""
    sha256 = hashlib.sha256()

    _debug_print(f"Computing combined hash for:")
    _debug_print(f"  Core.dll: {core_dll}")
    _debug_print(f"  level0: {level0}")

    # Hash Core.dll
    with open(core_dll, 'rb') as f:
        data = f.read()
        sha256.update(data)
        _debug_print(f"  Core.dll size: {len(data):,} bytes")

    # Hash level0
    with open(level0, 'rb') as f:
        data = f.read()
        sha256.update(data)
        _debug_print(f"  level0 size: {len(data):,} bytes")

    result = sha256.hexdigest()
    _debug_print(f"  Combined hash: {result}")
    return result


def decompile_dll(core_dll: Path, output_dir: Path) -> Optional[Path]:
    """Decompile Core.dll using ilspycmd"""
    _debug_print(f"Decompiling DLL: {core_dll}")
    _debug_print(f"  Output directory: {output_dir}")

    if output_dir.exists():
        _debug_print("  Cleaning existing output directory")
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir / "Core.decompiled.cs"

    # ilspycmd is in ~/.dotnet/tools
    ilspycmd = Path.home() / ".dotnet/tools/ilspycmd"
    if not ilspycmd.exists():
        ilspycmd = "ilspycmd"  # Try PATH
    _debug_print(f"  Using ilspycmd: {ilspycmd}")

    _debug_print(f"  Running: {ilspycmd} {core_dll} -o {output_file}")
    result = subprocess.run(
        [str(ilspycmd), str(core_dll), "-o", str(output_file)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        _debug_print(f"  Decompilation failed with code {result.returncode}")
        _debug_print(f"  stderr: {result.stderr}")
        raise RuntimeError(f"Decompilation failed: {result.stderr}")

    _debug_print(f"  Decompilation succeeded")

    # ilspycmd creates a directory with the same name, containing the .cs file
    actual_file = output_file / "Core.decompiled.cs"
    if actual_file.exists():
        _debug_print(f"  Found decompiled file: {actual_file}")
        _debug_print(f"  File size: {actual_file.stat().st_size:,} bytes")
        return actual_file
    elif output_file.is_file():
        _debug_print(f"  Found decompiled file: {output_file}")
        _debug_print(f"  File size: {output_file.stat().st_size:,} bytes")
        return output_file
    else:
        _debug_print("  Error: Could not find decompiled file")
        raise RuntimeError("Could not find decompiled file")


def find_window_class(code: str) -> Dict[str, str]:
    """Find the Window class and its output field type"""
    offsets = {}

    # Look for hackmud.Window class specifically
    window_match = re.search(
        r'namespace hackmud\s*\{[^}]*?public class Window\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
        code, re.DOTALL
    )

    if window_match:
        offsets['window_class'] = 'Window'
        offsets['window_namespace'] = 'hackmud'
        offsets['output_class'] = window_match.group(1)
        _debug_print(f"Found Window class: hackmud.Window")
        _debug_print(f"Found output type: {offsets['output_class']}")
    else:
        # Alternative: Find any class with gui_text field
        gui_text_match = re.search(
            r'public class (\w+)\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
            code, re.DOTALL
        )
        if gui_text_match:
            offsets['window_class'] = gui_text_match.group(1)
            offsets['output_class'] = gui_text_match.group(2)
            _debug_print(f"Found Window class: {offsets['window_class']}")
            _debug_print(f"Found output type: {offsets['output_class']}")

    return offsets


def find_queue_class(code: str, output_class: str) -> Dict[str, str]:
    """Find the Queue<string> field in the output class"""
    offsets = {}

    # Find the output class definition
    pattern = rf'public class {output_class}\s*\{{.*?public Queue<string> (\w+)\s*='
    match = re.search(pattern, code, re.DOTALL)

    if match:
        offsets['queue_field'] = match.group(1)
        _debug_print(f"Found Queue<string> field: {offsets['queue_field']}")

    return offsets


def generate_configs(output_dir: Path, game_path: Optional[Path] = None) -> Tuple[Path, Path, Path, Path]:
    """
    Generate all config files needed by the Scanner.

    Args:
        output_dir: Directory to write config files (usually CWD/data/)
        game_path: Optional game path (auto-detected if not provided)

    Returns:
        Tuple of (mono_offsets, scanner_config, mono_names_fixed, constants) paths
    """
    plat = platform.system()
    _debug_print(f"Platform: {plat}")

    # Detect game path
    if not game_path:
        game_path = detect_game_path()

    if not game_path or not game_path.exists():
        raise RuntimeError(
            "Could not detect game installation path. "
            "Install hackmud or set HACKMUD_PATH environment variable"
        )

    _debug_print(f"Game path: {game_path}")

    # Get Core.dll and level0 paths
    core_dll = get_core_dll_path(game_path, plat)
    level0_path = get_level0_path(game_path, plat)

    if not core_dll.exists():
        raise RuntimeError(f"Core.dll not found at {core_dll}")

    if not level0_path.exists():
        raise RuntimeError(f"level0 not found at {level0_path}")

    _debug_print(f"Core.dll: {core_dll}")
    _debug_print(f"level0: {level0_path}")

    # Decompile Core.dll
    temp_dir = Path("/tmp/hackmud_decompiled")
    decompiled_file = decompile_dll(core_dll, temp_dir)

    # Read decompiled code
    code = decompiled_file.read_text()

    # Extract class names
    class_info = find_window_class(code)
    if 'output_class' in class_info:
        class_info.update(find_queue_class(code, class_info['output_class']))

    # Compute checksum
    checksum = compute_combined_hash(core_dll, level0_path)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate mono_offsets.json
    mono_offsets = {
        "last_updated": "auto-generated",
        "class_names": {
            "window_class": class_info.get('window_class', 'Window'),
            "window_namespace": class_info.get('window_namespace', 'hackmud'),
            "output_class": class_info.get('output_class'),
            "queue_field": class_info.get('queue_field'),
            "kernel_class": "Kernel",
            "tmp_class": "TextMeshProUGUI",
            "tmp_namespace": "TMPro",
            "hardline_class": "HardlineCoordinator"
        },
        "mono_offsets": {
            "mono_class_name": "0x40",
            "mono_class_namespace": "0x48",
            "mono_class_runtime_info": "0xC8",
            "mono_runtime_info_vtable": "0x8",
            "mono_string_length": "0x10",
            "mono_string_data": "0x14"
        },
        "window_offsets": {
            "name": "0x90",
            "gui_text": "0x58"
        },
        "tmp_offsets": {
            "m_text": "0xc8"
        }
    }

    mono_offsets_file = output_dir / "mono_offsets.json"
    with open(mono_offsets_file, 'w') as f:
        json.dump(mono_offsets, f, indent=2)
    _debug_print(f"Generated: {mono_offsets_file}")

    # Generate scanner_config.json
    settings_path = DEFAULT_SETTINGS_PATHS.get(plat)
    config = {
        'platform': plat,
        'game_path': str(game_path),
        'checksum': checksum
    }
    if settings_path and settings_path.exists():
        config['settings_path'] = str(settings_path)

    scanner_config_file = output_dir / "scanner_config.json"
    with open(scanner_config_file, 'w') as f:
        json.dump(config, f, indent=2)
    _debug_print(f"Generated: {scanner_config_file}")

    # Generate mono_names_fixed.json
    mono_names_fixed = {
        "window_class": class_info.get('window_class', 'Window'),
        "window_namespace": class_info.get('window_namespace', 'hackmud'),
        "kernel_class": "Kernel",
        "tmp_class": "TextMeshProUGUI",
        "tmp_namespace": "TMPro",
        "hardline_class": "HardlineCoordinator"
    }

    mono_names_fixed_file = output_dir / "mono_names_fixed.json"
    with open(mono_names_fixed_file, 'w') as f:
        json.dump(mono_names_fixed, f, indent=2)
    _debug_print(f"Generated: {mono_names_fixed_file}")

    # Generate constants.json
    constants = {
        "version": "v2.016",  # Default, can be updated later
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

    constants_file = output_dir / "constants.json"
    with open(constants_file, 'w') as f:
        json.dump(constants, f, indent=2)
    _debug_print(f"Generated: {constants_file}")

    return mono_offsets_file, scanner_config_file, mono_names_fixed_file, constants_file

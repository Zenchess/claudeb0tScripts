#!/usr/bin/env python3
"""Update mono_reader offsets when hackmud recompiles

This script decompiles Core.dll and extracts the current obfuscated class names
for the terminal output structures. Run this after a game update to keep the
memory scanner working.

Usage:
    python3 update_offsets.py

Requirements:
    - ilspycmd (dotnet tool install -g ilspycmd)
    - Core.dll at the expected path
"""

import subprocess
import re
import json
import os
import hashlib
import platform
from pathlib import Path

# Debug flag from environment
DEBUG = os.getenv('HACKMUD_DEBUG', '').lower() in ('1', 'true', 'yes')

def _debug_print(*args, **kwargs):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print('[DEBUG update_offsets]', *args, **kwargs)

# Paths
OUTPUT_DIR = Path("/tmp/hackmud_decompiled")
OFFSETS_FILE = Path(__file__).parent / "mono_offsets.json"
CONFIG_FILE = Path(__file__).parent / "scanner_config.json"

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


def detect_game_path() -> Path:
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


def compute_dll_hash(dll_path: Path) -> str:
    """Compute SHA256 hash of Core.dll"""
    sha256 = hashlib.sha256()
    with open(dll_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_combined_hash(core_dll: Path, level0: Path) -> str:
    """Compute combined SHA256 hash of Core.dll and level0 files"""
    sha256 = hashlib.sha256()

    # Hash Core.dll
    with open(core_dll, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    # Hash level0
    with open(level0, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def decompile_dll(core_dll: Path):
    """Decompile Core.dll using ilspycmd"""
    import shutil
    _debug_print(f"Decompiling DLL: {core_dll}")
    _debug_print(f"  Output directory: {OUTPUT_DIR}")

    if OUTPUT_DIR.exists():
        _debug_print("  Cleaning existing output directory")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "Core.decompiled.cs"

    print(f"Decompiling {core_dll}...")
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
        print(f"Error: {result.stderr}")
        return None

    _debug_print(f"  Decompilation succeeded")

    # ilspycmd creates a directory with the same name, containing the .cs file
    actual_file = output_file / "Core.decompiled.cs"
    if actual_file.exists():
        _debug_print(f"  Found decompiled file: {actual_file}")
        _debug_print(f"  File size: {actual_file.stat().st_size:,} bytes")
        print(f"Decompiled to {actual_file}")
        return actual_file
    elif output_file.is_file():
        _debug_print(f"  Found decompiled file: {output_file}")
        _debug_print(f"  File size: {output_file.stat().st_size:,} bytes")
        print(f"Decompiled to {output_file}")
        return output_file
    else:
        _debug_print("  Error: Could not find decompiled file")
        print(f"Error: Could not find decompiled file")
        return None

def find_window_class(code: str) -> dict:
    """Find the Window class and its output field type"""
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

def find_queue_class(code: str, output_class: str) -> dict:
    """Find the Queue<string> field in the output class"""
    offsets = {}

    # Find the output class definition
    pattern = rf'public class {output_class}\s*\{{.*?public Queue<string> (\w+)\s*='
    match = re.search(pattern, code, re.DOTALL)

    if match:
        offsets['queue_field'] = match.group(1)
        print(f"Found Queue<string> field: {offsets['queue_field']}")

    return offsets

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Update hackmud memory scanner offsets')
    parser.add_argument('--game-path', type=str, help='Path to hackmud game folder')
    parser.add_argument('--settings-path', type=str, help='Path to hackmud settings folder')
    args = parser.parse_args()

    plat = platform.system()

    # Get game path
    if args.game_path:
        game_path = Path(args.game_path)
    else:
        game_path = detect_game_path()

    if not game_path or not game_path.exists():
        print("Could not detect game installation path.")
        print(f"Please provide --game-path argument")
        print(f"Example (Linux): --game-path ~/.local/share/Steam/steamapps/common/hackmud")
        print(f"Example (Windows): --game-path \"C:/Program Files (x86)/Steam/steamapps/common/hackmud\"")
        return

    print(f"Game path: {game_path}")

    # Get settings path
    if args.settings_path:
        settings_path = Path(args.settings_path)
    else:
        settings_path = DEFAULT_SETTINGS_PATHS.get(plat)
        if settings_path and not settings_path.exists():
            settings_path = None

    if settings_path:
        print(f"Settings path: {settings_path}")
    else:
        print(f"Settings path not detected (will use default)")

    # Generate Core.dll path
    core_dll = get_core_dll_path(game_path, plat)

    if not core_dll.exists():
        print(f"Error: Core.dll not found at {core_dll}")
        print("Make sure hackmud is installed and game path is correct")
        return

    print(f"Core.dll: {core_dll}")

    # Decompile
    output_file = decompile_dll(core_dll)
    if not output_file or not output_file.exists():
        print("Decompilation failed")
        return

    # Read decompiled code
    code = output_file.read_text()

    # Find class names
    class_info = {}
    class_info.update(find_window_class(code))

    if 'output_class' in class_info:
        class_info.update(find_queue_class(code, class_info['output_class']))

    # Get level0 path
    if plat == 'Linux':
        level0_path = game_path / "hackmud_lin_Data/level0"
    elif plat == 'Windows':
        level0_path = game_path / "hackmud_Data/level0"
    elif plat == 'Darwin':
        level0_path = game_path / "hackmud.app/Contents/Resources/Data/level0"
    else:
        raise ValueError(f"Unsupported platform: {plat}")

    if not level0_path.exists():
        print(f"Error: level0 not found at {level0_path}")
        return

    # Compute combined checksum of Core.dll and level0
    checksum = compute_combined_hash(core_dll, level0_path)
    print(f"\nPlatform: {plat}")
    print(f"Combined checksum (Core.dll + level0): {checksum[:16]}...")

    # Create config (user-specific settings)
    config = {
        'platform': plat,
        'game_path': str(game_path),
        'checksum': checksum
    }
    if settings_path:
        config['settings_path'] = str(settings_path)

    # Save config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Config saved to {CONFIG_FILE}")

    # Update offsets file (only class names, not user config)
    # Read existing offsets to preserve version/metadata
    if OFFSETS_FILE.exists():
        with open(OFFSETS_FILE, 'r') as f:
            offsets = json.load(f)
    else:
        offsets = {}

    # Update class names only
    offsets['class_names'] = {
        'window_class': class_info.get('window_class'),
        'window_namespace': class_info.get('window_namespace'),
        'output_class': class_info.get('output_class'),
        'queue_field': class_info.get('queue_field'),
        'kernel_class': offsets.get('class_names', {}).get('kernel_class', 'Kernel'),
        'tmp_class': offsets.get('class_names', {}).get('tmp_class', 'TextMeshProUGUI'),
        'tmp_namespace': offsets.get('class_names', {}).get('tmp_namespace', 'TMPro'),
        'hardline_class': offsets.get('class_names', {}).get('hardline_class', 'HardlineCoordinator'),
        'hardline_ip_field': offsets.get('class_names', {}).get('hardline_ip_field')
    }

    # Save offsets
    with open(OFFSETS_FILE, 'w') as f:
        json.dump(offsets, f, indent=2)
    print(f"Offsets saved to {OFFSETS_FILE}")

    # Extract and save window names to constants.json
    constants_file = Path(__file__).parent / "constants.json"
    try:
        # Get level0 path
        if plat == 'Linux':
            level0_path = game_path / "hackmud_lin_Data/level0"
        elif plat == 'Windows':
            level0_path = game_path / "hackmud_Data/level0"
        elif plat == 'Darwin':
            level0_path = game_path / "hackmud.app/Contents/Resources/Data/level0"
        else:
            raise ValueError(f"Unsupported platform: {plat}")

        if not level0_path.exists():
            print(f"Warning: level0 not found at {level0_path}")
            print("Skipping window name extraction")
        else:
            # Extract window names using UnityPy
            try:
                import UnityPy
                env = UnityPy.load(str(level0_path))

                window_names = set()
                known_windows = ['shell', 'chat', 'badge', 'breach', 'scratch', 'binlog', 'binmat', 'version']

                # Extract window names from level0
                for obj in env.objects:
                    if obj.type.name == "GameObject":
                        data = obj.read()
                        name = data.m_Name
                        if name.lower() in known_windows:
                            window_names.add(name)

                # Try to extract version from game memory (if game is running)
                game_version = "unknown"
                try:
                    # Import scanner module
                    import sys
                    sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))
                    from hackmud.memory.scanner import Scanner

                    print("\nAttempting to extract version from game memory...")
                    scanner = Scanner()
                    scanner.connect()
                    game_version = scanner.get_version()
                    print(f"✓ Version extracted from memory: {game_version}")
                    scanner.disconnect()
                except Exception as e:
                    print(f"ℹ Could not extract version from memory: {e}")
                    print(f"  (This is normal if game is not running)")
                    print(f"  Version will be set to 'unknown' in constants.json")

                # Save to constants.json
                constants = {
                    "version": game_version,
                    "window_names": sorted(window_names)
                }

                with open(constants_file, 'w') as f:
                    json.dump(constants, f, indent=2)
                print(f"Window names extracted: {sorted(window_names)}")
                print(f"Game version extracted: {game_version}")
                print(f"Constants saved to {constants_file}")

            except ImportError:
                print("Warning: UnityPy not installed. Install with: pip install UnityPy")
                print("Skipping window name extraction")
    except Exception as e:
        print(f"Warning: Failed to extract window names: {e}")
        print("Scanner will fall back to existing constants.json if available")

if __name__ == '__main__':
    main()

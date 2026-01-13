#!/usr/bin/env python3
"""Hackmud Memory Scanner - Setup and Configuration Manager

This script helps end users set up the memory scanner by:
- Checking system requirements
- Validating configuration
- Guiding through initial setup
- Providing clear next steps

Usage:
    python3 start.py
"""

import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple


def print_header():
    """Print welcome header"""
    print("=" * 70)
    print("Hackmud Memory Scanner - Setup Manager")
    print("=" * 70)
    print()


def check_python_version() -> bool:
    """Check if Python version is 3.6+"""
    print("[1/5] Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"    ❌ Python {version.major}.{version.minor} detected")
        print(f"    Required: Python 3.6 or higher")
        print(f"    Please upgrade Python and try again")
        return False
    print(f"    ✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_ilspycmd() -> bool:
    """Check if ilspycmd is installed"""
    print("[2/5] Checking ilspycmd (IL decompiler)...")

    # Check in ~/.dotnet/tools first
    ilspycmd_path = Path.home() / ".dotnet/tools/ilspycmd"
    if ilspycmd_path.exists():
        print(f"    ✅ Found at {ilspycmd_path}")
        return True

    # Try PATH
    try:
        result = subprocess.run(
            ["ilspycmd", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"    ✅ Found in PATH")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("    ❌ ilspycmd not found")
    print()
    print("    ilspycmd is required to decompile Core.dll")
    print("    Install with: dotnet tool install -g ilspycmd")
    print()
    print("    If you don't have .NET SDK:")
    print("    - Linux: sudo apt install dotnet-sdk-8.0")
    print("    - Windows: https://dotnet.microsoft.com/download")
    print("    - macOS: brew install dotnet")
    return False


def check_config_exists() -> Tuple[bool, Optional[Path]]:
    """Check if scanner_config.json exists"""
    print("[3/5] Checking configuration...")
    config_file = Path(__file__).parent / "scanner_config.json"

    if config_file.exists():
        print(f"    ✅ Config found: {config_file}")
        return True, config_file
    else:
        print(f"    ⚠️  Config not found: {config_file}")
        return False, config_file


def validate_config(config_file: Path) -> bool:
    """Validate scanner_config.json contents"""
    print("[4/5] Validating configuration...")

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("    ❌ Config file is corrupted (invalid JSON)")
        return False
    except Exception as e:
        print(f"    ❌ Error reading config: {e}")
        return False

    # Check required fields
    required_fields = ['platform', 'game_path', 'core_dll_hash']
    missing = [f for f in required_fields if f not in config]

    if missing:
        print(f"    ❌ Missing required fields: {', '.join(missing)}")
        return False

    # Check platform matches
    current_platform = platform.system()
    config_platform = config.get('platform', '')

    if current_platform != config_platform:
        print(f"    ⚠️  Platform mismatch!")
        print(f"        Config: {config_platform}")
        print(f"        Current: {current_platform}")
        print(f"        You need to regenerate config for {current_platform}")
        return False

    # Check game path exists
    game_path = Path(config['game_path'])
    if not game_path.exists():
        print(f"    ❌ Game path not found: {game_path}")
        print(f"        Please update game_path in config or regenerate")
        return False

    print(f"    ✅ Platform: {config_platform}")
    print(f"    ✅ Game path: {game_path}")
    print(f"    ✅ Config is valid")
    return True


def check_offsets_file() -> bool:
    """Check if mono_offsets.json exists"""
    print("[5/5] Checking offset definitions...")
    offsets_file = Path(__file__).parent / "mono_offsets.json"

    if offsets_file.exists():
        try:
            with open(offsets_file, 'r') as f:
                offsets = json.load(f)

            # Check for essential sections
            if 'class_names' in offsets and 'mono_offsets' in offsets:
                print(f"    ✅ Offsets file valid: {offsets_file}")
                return True
            else:
                print(f"    ⚠️  Offsets file incomplete")
                return False
        except:
            print(f"    ❌ Offsets file corrupted")
            return False
    else:
        print(f"    ❌ Offsets file not found: {offsets_file}")
        return False


def print_setup_instructions():
    """Print instructions for running update_offsets.py"""
    print()
    print("=" * 70)
    print("SETUP REQUIRED")
    print("=" * 70)
    print()
    print("To generate the configuration, run:")
    print()
    print("    python3 update_offsets.py")
    print()
    print("This will:")
    print("  • Auto-detect your hackmud installation (or prompt for path)")
    print("  • Decompile Core.dll to extract class names")
    print("  • Generate scanner_config.json with your platform settings")
    print("  • Update mono_offsets.json with current game structure")
    print()
    print("After setup completes, run this script again to validate.")
    print()


def print_success():
    """Print success message and next steps"""
    print()
    print("=" * 70)
    print("✅ SETUP COMPLETE - Ready to use!")
    print("=" * 70)
    print()
    print("Next steps:")
    print()
    print("1. Start hackmud")
    print()
    print("2. Read game terminal:")
    print("   python3 read_vtable.py 30")
    print()
    print("3. Read chat window:")
    print("   python3 read_vtable.py 20 --chat")
    print()
    print("4. Check other windows:")
    print("   python3 read_vtable.py --badge")
    print("   python3 read_vtable.py --breach")
    print()
    print("For more information, see CLAUDE.md")
    print()


def main():
    """Main setup validation flow"""
    print_header()

    # Step 1: Check Python version
    if not check_python_version():
        return 1
    print()

    # Step 2: Check ilspycmd
    if not check_ilspycmd():
        return 1
    print()

    # Step 3: Check config exists
    config_exists, config_file = check_config_exists()
    print()

    if not config_exists:
        # Step 4 & 5: Skip if no config
        print("[4/5] ⏭️  Skipped (no config)")
        print()
        print("[5/5] ⏭️  Skipped (no config)")
        print()
        print_setup_instructions()
        return 1

    # Step 4: Validate config
    if not validate_config(config_file):
        print()
        print_setup_instructions()
        return 1
    print()

    # Step 5: Check offsets file
    if not check_offsets_file():
        print()
        print_setup_instructions()
        return 1
    print()

    # All checks passed!
    print_success()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

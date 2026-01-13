#!/usr/bin/env python3
"""Test the updated Scanner.get_version() method"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def test_get_version():
    print("Testing Scanner.get_version() with pattern search...")
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"✓ Connected to PID {scanner.pid}")
        print()

        print("Calling scanner.get_version()...")
        version = scanner.get_version()

        print(f"✓ Version: {version}")
        print()
        print("SUCCESS: get_version() works with pattern search!")

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    finally:
        scanner.close()

    return True

if __name__ == "__main__":
    success = test_get_version()
    sys.exit(0 if success else 1)

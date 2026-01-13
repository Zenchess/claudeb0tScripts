#!/usr/bin/env python3
"""Test the Scanner.get_version() method"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def test_get_version():
    scanner = Scanner()
    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}")

        version = scanner.get_version()
        print(f"Version: {version}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scanner.close()

if __name__ == "__main__":
    test_get_version()

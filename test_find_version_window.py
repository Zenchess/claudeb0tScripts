#!/usr/bin/env python3
"""Test finding the version window directly"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def test_find_version_window():
    scanner = Scanner()
    scanner.set_debug(True)  # Enable debug output

    try:
        scanner.connect()
        print(f"\nConnected to PID {scanner.pid}\n")

        # Try to find version window
        print("Attempting to find 'version' window...")
        version_window_addr = scanner._find_window('version')

        if version_window_addr:
            print(f"✓ Found version window at {hex(version_window_addr)}")

            # Try to read it
            lines = scanner.read_window('version', lines=5, preserve_colors=False)
            print(f"\nVersion window content:")
            for line in lines:
                print(f"  {line}")
        else:
            print("✗ Version window not found")

            # List what windows ARE available
            print("\nSearching for other windows...")
            for window_name in ['shell', 'chat', 'badge', 'breach', 'scratch', 'version']:
                addr = scanner._find_window(window_name)
                if addr:
                    print(f"  ✓ Found '{window_name}' at {hex(addr)}")
                else:
                    print(f"  ✗ '{window_name}' not found")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scanner.close()

if __name__ == "__main__":
    test_find_version_window()

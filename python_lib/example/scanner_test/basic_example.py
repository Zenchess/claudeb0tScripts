#!/usr/bin/env python3
"""
Simple example demonstrating the hackmud Scanner API.

This example shows:
1. Connecting to the hackmud process
2. Reading the game version
3. Reading game windows (shell and chat)
4. Proper cleanup with close()
"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hackmud.memory import Scanner


def main():
    print("=" * 60)
    print("Hackmud Scanner API - Basic Example")
    print("=" * 60)
    print()

    # Create scanner instance
    scanner = Scanner()

    try:
        # 1. Connect to hackmud process
        print("[1] Connecting to hackmud...")
        scanner.connect()
        print(f"    ✓ Connected to PID {scanner.pid}")
        print()

        # 2. Get game version
        print("[2] Reading game version...")
        version = scanner.get_version()
        print(f"    ✓ Version: {version}")
        print()

        # 3. Read shell output
        print("[3] Reading shell terminal (last 10 lines)...")
        shell_lines = scanner.read_window('shell', lines=10)
        print(f"    ✓ Read {len(shell_lines)} lines from shell")
        print()
        print("    Shell output:")
        for line in shell_lines:
            print(f"      {line}")
        print()

        # 4. Read chat output
        print("[4] Reading chat window (last 5 lines)...")
        chat_lines = scanner.read_window('chat', lines=5)
        print(f"    ✓ Read {len(chat_lines)} lines from chat")
        print()
        print("    Chat output:")
        for line in chat_lines:
            print(f"      {line}")
        print()

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # 5. Always clean up
        print("[5] Disconnecting...")
        scanner.close()
        print("    ✓ Closed connection")
        print()

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

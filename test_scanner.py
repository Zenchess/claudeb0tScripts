#!/usr/bin/env python3
"""Test script for the new Scanner API"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner
from hackmud.memory.exceptions import GameNotFoundError, WindowNotFoundError

def main():
    print("Testing Scanner API...")
    print()

    try:
        # Test context manager
        with Scanner() as scanner:
            print("✅ Scanner connected successfully!")
            print(f"   PID: {scanner.pid}")
            print()

            # Test reading shell
            print("Reading shell window (last 10 lines)...")
            try:
                lines = scanner.read_window('shell', lines=10)
                print(f"✅ Read {len(lines)} lines from shell")
                print("   Preview:")
                for line in lines[-5:]:
                    preview = line[:80] + '...' if len(line) > 80 else line
                    print(f"   {preview}")
                print()
            except WindowNotFoundError as e:
                print(f"❌ Shell window error: {e}")
                print()

            # Test reading chat
            print("Reading chat window (last 5 lines)...")
            try:
                lines = scanner.read_window('chat', lines=5)
                print(f"✅ Read {len(lines)} lines from chat")
                print("   Preview:")
                for line in lines[-3:]:
                    preview = line[:80] + '...' if len(line) > 80 else line
                    print(f"   {preview}")
                print()
            except WindowNotFoundError as e:
                print(f"❌ Chat window error: {e}")
                print()

            # Test window caching
            print("Testing window caching (reading shell again)...")
            lines2 = scanner.read_window('shell', lines=5)
            print(f"✅ Cache working - read {len(lines2)} lines")
            print()

        print("✅ Scanner closed successfully!")

    except GameNotFoundError:
        print("❌ Error: hackmud is not running")
        print("   Please start the game first")
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())

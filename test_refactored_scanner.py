#!/usr/bin/env python3
"""Test refactored scanner with dynamic window name extraction"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner

print("Testing refactored scanner with dynamic window name extraction...")
print()

try:
    with Scanner() as scanner:
        print(f"✅ Scanner connected successfully")
        print(f"✅ Window names detected: {scanner.constants['window_names']}")
        print()

        # Test reading shell window
        print("Testing shell window read...")
        lines = scanner.read_window('shell', lines=5)
        print(f"✅ Read {len(lines)} lines from shell")
        print()

        print("All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

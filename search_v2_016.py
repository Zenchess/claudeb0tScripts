#!/usr/bin/env python3
"""Search specifically for v2.016 pattern"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def search_v2_016():
    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Search for "v2.016" in UTF-16 LE
        pattern_016 = b'v\x002\x00.\x000\x001\x006\x00'
        pattern_16 = b'v\x002\x00.\x001\x006\x00'

        print("Searching for 'v2.016' (with leading zero)...")
        found_016 = False

        regions = scanner._get_memory_regions()

        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:
                continue

            try:
                data = mem.read(start, size)

                # Search for v2.016
                pos = data.find(pattern_016)
                if pos != -1:
                    found_016 = True
                    addr = start + pos
                    context = data[max(0, pos-32):min(len(data), pos+64)]
                    print(f"  ✓ Found 'v2.016' at {hex(addr)}")
                    print(f"    Context: {context.decode('utf-16le', errors='ignore')[:80]}")
                    print()

            except:
                pass

        if not found_016:
            print("  ✗ 'v2.016' not found in memory")

        print("\nSearching for 'v2.16' (without leading zero)...")
        found_16 = []

        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:
                continue

            try:
                data = mem.read(start, size)

                # Search for v2.16
                pos = 0
                while True:
                    pos = data.find(pattern_16, pos)
                    if pos == -1:
                        break

                    addr = start + pos
                    context = data[max(0, pos-32):min(len(data), pos+64)]
                    found_16.append((addr, context.decode('utf-16le', errors='ignore')[:80]))

                    if len(found_16) >= 5:
                        break
                    pos += 1

                if len(found_16) >= 5:
                    break

            except:
                pass

        if found_16:
            print(f"  ✓ Found {len(found_16)} instances of 'v2.16':")
            for addr, context in found_16[:5]:
                print(f"    {hex(addr)}: {context}")
        else:
            print("  ✗ 'v2.16' not found in memory")

    finally:
        scanner.close()

if __name__ == "__main__":
    search_v2_016()

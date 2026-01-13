#!/usr/bin/env python3
"""Search for pointers to nearby addresses around the MonoString"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def search_nearby():
    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Kaj's address
        base_addr = 0x7f1601d93c38

        # Try addresses nearby (different MonoString structure interpretations)
        test_addresses = [
            (base_addr, "base"),
            (base_addr - 0x8, "base - 0x8"),
            (base_addr - 0x10, "base - 0x10"),
            (base_addr - 0x20, "base - 0x20"),
            (base_addr + 0xc, "data start (base + 0xc)"),
        ]

        # Get memory regions
        maps_file = f"/proc/{scanner.pid}/maps"
        regions = []
        with open(maps_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and 'rw' in parts[1]:
                    addr_range = parts[0]
                    start, end = addr_range.split('-')
                    regions.append((int(start, 16), int(end, 16)))

        # Search for pointers to each test address
        for test_addr, desc in test_addresses:
            print(f"Searching for pointers to {hex(test_addr)} ({desc})...")

            ptr_bytes = struct.pack('<Q', test_addr)
            found_count = 0

            for start, end in regions[:50]:  # Check first 50 regions
                if found_count >= 5:  # Stop after finding 5
                    break

                size = end - start
                if size > 50 * 1024 * 1024:
                    continue

                try:
                    data = mem.read(start, size)
                    pos = 0
                    while True:
                        pos = data.find(ptr_bytes, pos)
                        if pos == -1:
                            break

                        ptr_addr = start + pos
                        print(f"  ✓ Found pointer at {hex(ptr_addr)}")
                        found_count += 1

                        if found_count >= 5:
                            break

                        pos += 8
                except:
                    pass

            if found_count == 0:
                print(f"  ✗ No pointers found")

            print()

    finally:
        scanner.close()

if __name__ == "__main__":
    search_nearby()

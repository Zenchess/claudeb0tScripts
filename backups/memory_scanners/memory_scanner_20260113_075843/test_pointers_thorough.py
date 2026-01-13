#!/usr/bin/env python3
"""Thorough search for pointers to version MonoString - check ALL regions"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def thorough_pointer_search():
    print("=" * 70)
    print("Thorough search for pointers to version MonoString")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Test multiple MonoString base addresses
        # We know the data is at 0x7f1601d93c44
        # MonoString structures we found: length at +0x8, data at +0xc
        # So base would be at data - 0xc = 0x7f1601d93c44 - 0xc = 0x7f1601d93c38

        test_addresses = [
            (0x7f1601d93c38, "MonoString base (length at +0x8, data at +0xc)"),
            (0x7f1601d93c44, "String data address"),
            (0x7f1601d93c34, "MonoString base (length at +0x10, data at +0x14)"),
            (0x7f1601d93c24, "MonoString base (length at +0x10, data at +0x20)"),
        ]

        # Get ALL memory regions (don't skip any)
        maps_file = f"/proc/{scanner.pid}/maps"
        all_regions = []
        with open(maps_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and 'rw' in parts[1]:
                    addr_range = parts[0]
                    start, end = addr_range.split('-')
                    all_regions.append((int(start, 16), int(end, 16)))

        print(f"Scanning {len(all_regions)} RW memory regions")
        print()

        for test_addr, desc in test_addresses:
            print(f"Searching for pointers to {hex(test_addr)} ({desc})...")

            ptr_bytes = struct.pack('<Q', test_addr)
            found_count = 0
            found_locations = []

            for i, (start, end) in enumerate(all_regions):
                size = end - start

                # Show progress for large scans
                if i % 50 == 0:
                    print(f"  Scanning region {i+1}/{len(all_regions)} ({hex(start)}-{hex(end)}, {size} bytes)...")

                # Skip extremely large regions (> 500MB) to avoid timeouts
                if size > 500 * 1024 * 1024:
                    print(f"  Skipping huge region: {size // (1024*1024)} MB")
                    continue

                try:
                    # Read in chunks for large regions
                    chunk_size = min(10 * 1024 * 1024, size)  # 10MB chunks
                    for offset in range(0, size, chunk_size):
                        read_addr = start + offset
                        read_size = min(chunk_size, end - read_addr)

                        data = mem.read(read_addr, read_size)

                        pos = 0
                        while True:
                            pos = data.find(ptr_bytes, pos)
                            if pos == -1:
                                break

                            ptr_location = read_addr + pos
                            found_locations.append(ptr_location)
                            found_count += 1

                            if found_count <= 10:  # Print first 10
                                print(f"  ✓ Found pointer at {hex(ptr_location)}")

                            if found_count >= 50:  # Stop after 50
                                break

                            pos += 8

                        if found_count >= 50:
                            break

                except Exception as e:
                    # Don't stop on errors, just skip this region
                    pass

                if found_count >= 50:
                    break

            if found_count == 0:
                print(f"  ✗ No pointers found")
            else:
                print(f"  Total: {found_count} pointers found")

                # For each pointer, check if it could be Text.m_Text
                print(f"\n  Analyzing first 10 pointer locations:")
                for ptr_loc in found_locations[:10]:
                    print(f"    Pointer at {hex(ptr_loc)}:")

                    # Try different offsets for Text.m_Text
                    for m_text_offset in [0xd0, 0xc8, 0xb8, 0xc0]:
                        text_obj = ptr_loc - m_text_offset
                        print(f"      If m_Text at +{hex(m_text_offset)}, Text object at {hex(text_obj)}")

            print()

        print("=" * 70)
        print("Thorough search complete")
        print("=" * 70)

    finally:
        scanner.close()

if __name__ == "__main__":
    thorough_pointer_search()

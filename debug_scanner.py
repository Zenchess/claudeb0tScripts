#!/usr/bin/env python3
"""Debug scanner to find why windows aren't being discovered"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

print(f"PID: {scanner.pid}")
print()

# Find Window vtable
print("Finding Window vtable...")
vtable = scanner._find_window_vtable()
print(f"Window vtable: 0x{vtable:x}" if vtable else "Window vtable: NOT FOUND")
print()

# Get memory regions
print("Getting memory regions...")
regions = scanner._get_memory_regions()
print(f"Found {len(regions)} rw- regions")
print()

# Search for vtable in regions
if vtable:
    vtable_bytes = struct.pack('<Q', vtable)
    print(f"Searching for vtable bytes: {vtable_bytes.hex()}")
    total_matches = 0

    for i, (start, end) in enumerate(regions[:10]):  # Check first 10 regions
        try:
            data = scanner.memory_reader.read(start, end - start)
            count = data.count(vtable_bytes)
            if count > 0:
                print(f"  Region {i}: 0x{start:x}-0x{end:x} - {count} matches")
                total_matches += count
        except Exception as e:
            print(f"  Region {i}: Failed to read - {e}")

    print(f"\nTotal vtable matches in first 10 regions: {total_matches}")
    print()

    # Try manual scan
    print("Manual window scan in first region with matches...")
    for start, end in regions:
        try:
            data = scanner.memory_reader.read(start, end - start)
            pos = data.find(vtable_bytes)
            if pos != -1:
                window_addr = start + pos
                print(f"Found potential window at: 0x{window_addr:x}")

                # Try to read window name
                try:
                    name_offset = scanner.offsets.get('window_name', 0x90)
                    name_ptr = scanner._read_pointer(window_addr + name_offset)
                    print(f"  Name pointer: 0x{name_ptr:x}" if name_ptr else "  Name pointer: NULL")

                    if name_ptr and name_ptr != 0:
                        name = scanner._read_mono_string(name_ptr)
                        print(f"  Name: {repr(name)}")
                except Exception as e:
                    print(f"  Error reading name: {e}")

                break  # Just check first match
        except:
            continue

scanner.close()

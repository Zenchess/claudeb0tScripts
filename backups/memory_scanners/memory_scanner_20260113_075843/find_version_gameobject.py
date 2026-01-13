#!/usr/bin/env python3
"""Search for Unity GameObject named 'version'"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def find_version_gameobject():
    print("=" * 70)
    print("Searching for GameObject named 'version'")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

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

        # Search for "version" string (ASCII and UTF-16)
        version_ascii = b'version\x00'
        version_utf16 = 'version'.encode('utf-16-le') + b'\x00\x00'

        print("Step 1: Finding 'version' string in memory...")
        found_strings = []

        for start, end in regions:
            if len(found_strings) >= 10:
                break

            size = end - start
            if size > 100 * 1024 * 1024:
                continue

            try:
                data = mem.read(start, size)

                # Search ASCII
                pos = data.find(version_ascii)
                if pos != -1:
                    addr = start + pos
                    found_strings.append((addr, "ASCII"))
                    print(f"  ✓ Found 'version' (ASCII) at {hex(addr)}")
                    if len(found_strings) >= 10:
                        break

                # Search UTF-16
                pos = 0
                while True:
                    pos = data.find(version_utf16, pos)
                    if pos == -1:
                        break
                    addr = start + pos
                    found_strings.append((addr, "UTF-16"))
                    print(f"  ✓ Found 'version' (UTF-16) at {hex(addr)}")
                    if len(found_strings) >= 10:
                        break
                    pos += 1
            except:
                pass

        if not found_strings:
            print("  ✗ No 'version' strings found")
            return False

        print(f"\nFound {len(found_strings)} 'version' strings")
        print()

        # Step 2: Search for GameObject instances that reference these strings
        print("Step 2: Searching for GameObject references to 'version' string...")

        for string_addr, string_type in found_strings[:5]:
            print(f"\nChecking references to {hex(string_addr)} ({string_type}):")

            # Search for pointers to this string
            ptr_bytes = struct.pack('<Q', string_addr)
            found_refs = []

            for start, end in regions:
                if len(found_refs) >= 5:
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

                        ref_addr = start + pos
                        found_refs.append(ref_addr)
                        print(f"  → Pointer at {hex(ref_addr)}")

                        if len(found_refs) >= 5:
                            break
                        pos += 8
                except:
                    pass

            if not found_refs:
                print(f"  ✗ No references found")
            else:
                print(f"  Found {len(found_refs)} references")

                # For each reference, try to identify GameObject structure
                for ref_addr in found_refs[:3]:
                    # GameObject.name is typically at an offset from GameObject base
                    # Try common offsets
                    for name_offset in [0x18, 0x20, 0x28, 0x30, 0x10]:
                        gameobject_addr = ref_addr - name_offset
                        print(f"    If GameObject.name at +{hex(name_offset)}, GameObject at {hex(gameobject_addr)}")

                        # Try to read some data around this potential GameObject
                        try:
                            obj_data = mem.read(gameobject_addr, 128)
                            # Check for vtable pointer at +0x0
                            vtable = struct.unpack('<Q', obj_data[0:8])[0]
                            if vtable > 0x1000 and vtable < 0x7fffffffffff:
                                print(f"      ✓ Valid vtable: {hex(vtable)}")
                        except:
                            pass

        print()
        print("=" * 70)
        print("Search complete")
        print("=" * 70)

    finally:
        scanner.close()

if __name__ == "__main__":
    find_version_gameobject()

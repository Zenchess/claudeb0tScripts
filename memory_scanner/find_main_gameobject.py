#!/usr/bin/env python3
"""Search for GameObject 'Main' and its child 'version' in Unity scene hierarchy"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def find_main_and_children():
    print("=" * 70)
    print("Searching for GameObject 'Main' and its children")
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

        # Search for "Main" string (ASCII and UTF-16)
        main_ascii = b'Main\x00'
        main_utf16 = 'Main'.encode('utf-16-le') + b'\x00\x00'

        print("Step 1: Finding 'Main' string in memory...")
        found_main_strings = []

        for start, end in regions:
            if len(found_main_strings) >= 20:
                break

            size = end - start
            if size > 100 * 1024 * 1024:  # Skip huge regions
                continue

            try:
                data = mem.read(start, size)

                # Search ASCII
                pos = 0
                while True:
                    pos = data.find(main_ascii, pos)
                    if pos == -1:
                        break
                    addr = start + pos
                    found_main_strings.append((addr, "ASCII"))
                    print(f"  ✓ Found 'Main' (ASCII) at {hex(addr)}")
                    if len(found_main_strings) >= 20:
                        break
                    pos += 1

                # Search UTF-16
                pos = 0
                while True:
                    pos = data.find(main_utf16, pos)
                    if pos == -1:
                        break
                    addr = start + pos
                    found_main_strings.append((addr, "UTF-16"))
                    print(f"  ✓ Found 'Main' (UTF-16) at {hex(addr)}")
                    if len(found_main_strings) >= 20:
                        break
                    pos += 1
            except:
                pass

        if not found_main_strings:
            print("  ✗ No 'Main' strings found")
            return False

        print(f"\nFound {len(found_main_strings)} 'Main' strings")
        print()

        # Step 2: For each Main string, check for GameObject structure
        print("Step 2: Analyzing each 'Main' string for GameObject structure...")
        print()

        for string_addr, string_type in found_main_strings[:10]:
            print(f"[{string_type}] String at {hex(string_addr)}")

            # GameObject.name is typically at an offset from GameObject base
            # Try common offsets
            for name_offset in [0x18, 0x20, 0x28, 0x30, 0x10, 0x38, 0x40]:
                gameobject_addr = string_addr - name_offset

                try:
                    # Read potential GameObject
                    obj_data = mem.read(gameobject_addr, 512)

                    # Check for vtable pointer at +0x0
                    vtable = struct.unpack('<Q', obj_data[0:8])[0]
                    if not (0x1000 < vtable < 0x7fffffffffff):
                        continue

                    print(f"  Potential GameObject at {hex(gameobject_addr)}")
                    print(f"    Name at +{hex(name_offset)}")
                    print(f"    Vtable: {hex(vtable)}")

                    # GameObject has a Transform component reference
                    # Transform component handles parent-child relationships
                    # Common offsets for m_GameObject (in Transform): +0x30, +0x38, +0x40

                    # Show structure around potential GameObject
                    print(f"    First 256 bytes of structure:")
                    for i in range(0, 256, 16):
                        hex_str = ' '.join(f'{b:02x}' for b in obj_data[i:i+16])
                        offset_label = f"+{i:03x}"

                        # Try to decode any pointers
                        if i + 8 <= len(obj_data):
                            ptr_val = struct.unpack('<Q', obj_data[i:i+8])[0]
                            if 0x1000 < ptr_val < 0x7fffffffffff:
                                print(f"      {offset_label}: {hex_str}  [PTR: {hex(ptr_val)}]")
                            else:
                                print(f"      {offset_label}: {hex_str}")
                        else:
                            print(f"      {offset_label}: {hex_str}")

                    # Look for Transform component
                    print(f"\n    Searching for Transform component references:")
                    for i in range(0, 128, 8):
                        if i + 8 <= len(obj_data):
                            ptr_val = struct.unpack('<Q', obj_data[i:i+8])[0]
                            if 0x1000 < ptr_val < 0x7fffffffffff:
                                # Could be Transform reference
                                try:
                                    # Try to read the referenced object
                                    ref_data = mem.read(ptr_val, 128)
                                    ref_vtable = struct.unpack('<Q', ref_data[0:8])[0]
                                    if 0x1000 < ref_vtable < 0x7fffffffffff:
                                        print(f"      +{i:03x} -> {hex(ptr_val)} (vtable {hex(ref_vtable)})")
                                except:
                                    pass

                    print()

                except Exception as e:
                    pass

        print("==" * 35)
        print("Search complete")
        print("==" * 35)

    finally:
        scanner.close()

if __name__ == "__main__":
    find_main_and_children()

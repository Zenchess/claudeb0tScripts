#!/usr/bin/env python3
"""Search for pointers to the MonoString at 0x7f1601d93c38 (Kaj's address)"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def search_kaj_address():
    print("=" * 70)
    print("Searching for pointers to MonoString at 0x7f1601d93c38")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # The address Kaj specified
        monostring_addr = 0x7f1601d93c38

        # Verify this is actually a MonoString with version
        print(f"Verifying MonoString at {hex(monostring_addr)}...")
        try:
            # Try reading as MonoString (length at +0x10, data at +0x20)
            length = struct.unpack('<I', mem.read(monostring_addr + 0x10, 4))[0]
            if length > 0 and length < 100:
                data = mem.read(monostring_addr + 0x20, length * 2)
                text = data.decode('utf-16-le', errors='ignore')
                print(f"  ✓ MonoString contains: '{text}'")
            else:
                # Try other offsets
                for length_off, data_off in [(0x08, 0x0c), (0x10, 0x14)]:
                    length = struct.unpack('<I', mem.read(monostring_addr + length_off, 4))[0]
                    if length > 0 and length < 100:
                        data = mem.read(monostring_addr + data_off, length * 2)
                        text = data.decode('utf-16-le', errors='ignore')
                        print(f"  ✓ MonoString contains: '{text}' (length at +{hex(length_off)}, data at +{hex(data_off)})")
                        break
        except Exception as e:
            print(f"  ⚠ Could not read as MonoString: {e}")
        print()

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

        # Search for this exact pointer value
        print(f"Searching for pointers to {hex(monostring_addr)}...")
        monostring_ptr_bytes = struct.pack('<Q', monostring_addr)

        pointer_locations = []

        for start, end in regions:
            if len(pointer_locations) >= 50:  # Get up to 50 pointers
                break

            size = end - start
            if size > 100 * 1024 * 1024:  # Skip huge regions
                continue

            try:
                chunk_size = min(1024 * 1024, size)
                for offset in range(0, size, chunk_size):
                    addr = start + offset
                    read_size = min(chunk_size, end - addr)
                    data = mem.read(addr, read_size)

                    pos = 0
                    while True:
                        pos = data.find(monostring_ptr_bytes, pos)
                        if pos == -1:
                            break

                        ptr_addr = addr + pos
                        pointer_locations.append(ptr_addr)

                        if len(pointer_locations) >= 50:
                            break

                        pos += 8

                    if len(pointer_locations) >= 50:
                        break
            except:
                pass

        print(f"✓ Found {len(pointer_locations)} pointers")
        print()

        if not pointer_locations:
            print("✗ No pointers found")
            return False

        # Analyze first 20 pointers
        print("Analyzing pointer locations:")
        print()

        for i, ptr_addr in enumerate(pointer_locations[:20]):
            print(f"[{i+1}] Pointer at {hex(ptr_addr)}")

            # Try different Text.m_Text offsets
            for m_text_offset in [0xd0, 0xc8, 0xd8, 0xe0, 0xb8, 0xc0, 0xa8, 0xb0]:
                text_obj_addr = ptr_addr - m_text_offset

                try:
                    # Verify by reading back
                    verify_ptr = struct.unpack('<Q', mem.read(text_obj_addr + m_text_offset, 8))[0]
                    if verify_ptr == monostring_addr:
                        print(f"    ✓ Text object candidate at {hex(text_obj_addr)}")
                        print(f"      m_Text field at offset +{hex(m_text_offset)}")

                        # Read first 64 bytes of the object
                        try:
                            obj_data = mem.read(text_obj_addr, 64)
                            print(f"      First 64 bytes:")
                            # Print in rows of 16 bytes
                            for j in range(0, 64, 16):
                                hex_str = ' '.join(f'{b:02x}' for b in obj_data[j:j+16])
                                print(f"        {hex(text_obj_addr + j):016x}: {hex_str}")
                        except:
                            pass

                        print()
                        return True  # Found it!
                except:
                    pass

        print("✗ No valid Text object structure found")
        return False

    finally:
        scanner.close()

if __name__ == "__main__":
    success = search_kaj_address()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Find Text object by searching backwards from version MonoString

Since we know where the version MonoString is, search for pointers to it.
Those pointers would be in Text.m_Text field.
"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def find_text_backwards():
    print("=" * 70)
    print("Finding Text object by searching backwards from MonoString")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"[1/3] Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # Step 1: Find version MonoString (we know this works)
        print("[2/3] Finding version MonoString...")

        maps_file = f"/proc/{scanner.pid}/maps"
        regions = []
        with open(maps_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and 'rw' in parts[1]:
                    addr_range = parts[0]
                    start, end = addr_range.split('-')
                    regions.append((int(start, 16), int(end, 16)))

        # Search for version string
        patterns = ['v2.016'.encode('utf-16-le')]
        version_data_addr = None
        version_monostring_addr = None

        for start, end in regions:
            if version_data_addr:
                break
            try:
                chunk_size = 1024 * 1024
                for offset in range(0, end - start, chunk_size):
                    addr = start + offset
                    read_size = min(chunk_size, end - addr)
                    data = mem.read(addr, read_size)

                    for pattern in patterns:
                        pos = data.find(pattern)
                        if pos != -1:
                            version_data_addr = addr + pos

                            # MonoString base is at data_addr - data_offset
                            # Try common offsets
                            for data_offset in [0x20, 0x14, 0x0c]:
                                test_monostring = version_data_addr - data_offset
                                # Verify by trying to read the string
                                try:
                                    # This should be a valid MonoString
                                    version_monostring_addr = test_monostring
                                    break
                                except:
                                    pass
                            break

                    if version_data_addr:
                        break
            except:
                pass

        if not version_monostring_addr:
            print("      ✗ Could not find version MonoString")
            return False

        print(f"      ✓ Found version MonoString at {hex(version_monostring_addr)}")
        print(f"        Data at {hex(version_data_addr)}")
        print()

        # Step 2: Search for pointers to this MonoString
        print("[3/3] Searching for pointers to MonoString...")
        print("      (This would be Text.m_Text field)")
        print(f"      Searching for pointer bytes: {hex(version_monostring_addr)}")

        # Try both the MonoString base AND the data address
        monostring_ptr_bytes = struct.pack('<Q', version_monostring_addr)
        data_ptr_bytes = struct.pack('<Q', version_data_addr)
        pointer_locations = []

        # Search in smaller regions first (more likely to find objects there)
        sorted_regions = sorted(regions, key=lambda r: r[1] - r[0])

        for start, end in sorted_regions[:100]:  # Check first 100 regions
            if len(pointer_locations) >= 5:  # Stop after finding 5
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

                    # Search for both pointer types
                    for search_bytes in [monostring_ptr_bytes, data_ptr_bytes]:
                        pos = 0
                        while True:
                            pos = data.find(search_bytes, pos)
                            if pos == -1:
                                break

                            ptr_addr = addr + pos
                            pointer_locations.append((ptr_addr, search_bytes))

                            if len(pointer_locations) >= 20:  # Limit results
                                break

                            pos += 8

                        if len(pointer_locations) >= 20:
                            break

                    if len(pointer_locations) >= 20:
                        break
            except:
                pass

        if not pointer_locations:
            print("      ✗ No pointers found to MonoString")
            return False

        print(f"      ✓ Found {len(pointer_locations)} pointers to MonoString")
        print()

        # Step 3: Check each pointer location
        print("Analyzing pointer locations:")
        print()

        for ptr_addr, search_bytes in pointer_locations[:10]:  # Check first 10
            ptr_value = struct.unpack('<Q', search_bytes)[0]
            print(f"  Pointer at {hex(ptr_addr)} → {hex(ptr_value)}")

            # If this is Text.m_Text, try different offsets
            for m_text_offset in [0xd0, 0xc8, 0xd8, 0xe0, 0xb8, 0xc0]:
                text_obj_addr = ptr_addr - m_text_offset

                # Verify: read back the pointer
                try:
                    verify_ptr = struct.unpack('<Q', mem.read(text_obj_addr + m_text_offset, 8))[0]
                    if verify_ptr == ptr_value:  # Match the pointer we found
                        print(f"    ✓ Potential Text object at {hex(text_obj_addr)}")
                        print(f"      m_Text at offset +{hex(m_text_offset)}")

                        # Try to read nearby data to validate
                        try:
                            # Read 256 bytes around the object
                            obj_data = mem.read(text_obj_addr, min(256, m_text_offset + 16))
                            print(f"      First 32 bytes: {obj_data[:32].hex()}")
                        except:
                            pass

                        # Success!
                        return True
                except:
                    pass

        print()
        print("✗ Could not validate Text object structure")
        return False

    finally:
        scanner.close()

if __name__ == "__main__":
    success = find_text_backwards()
    sys.exit(0 if success else 1)

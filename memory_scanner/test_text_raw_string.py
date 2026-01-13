#!/usr/bin/env python3
"""Find Text object where m_Text contains the version string directly (raw string, not pointer)"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def find_text_with_raw_string():
    print("=" * 70)
    print("Finding Text object with m_Text containing raw version string")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # The version string as UTF-16-LE bytes
        version_pattern = b'v\x002\x00.\x000\x001\x006\x00'  # "v2.016" in UTF-16-LE
        print(f"Searching for version pattern (UTF-16-LE): {version_pattern.hex()}")
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

        # Search for the version string pattern
        found_locations = []

        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:  # Skip huge regions
                continue

            try:
                data = mem.read(start, size)
                pos = 0
                while True:
                    pos = data.find(version_pattern, pos)
                    if pos == -1:
                        break

                    string_addr = start + pos
                    found_locations.append(string_addr)

                    if len(found_locations) >= 20:  # Limit to 20
                        break

                    pos += 1

                if len(found_locations) >= 20:
                    break
            except:
                pass

        print(f"Found {len(found_locations)} occurrences of version string")
        print()

        if not found_locations:
            print("✗ No version strings found")
            return False

        # For each occurrence, try to find the Text object structure
        print("Analyzing each occurrence:")
        print()

        for i, string_addr in enumerate(found_locations[:10], 1):
            print(f"[{i}] Version string at {hex(string_addr)}")

            # If this is Text.m_Text field, the Text object is at string_addr - m_text_offset
            # Try different offsets for m_Text field
            for m_text_offset in [0xd0, 0xc8, 0xd8, 0xe0, 0xb8, 0xc0, 0xa8, 0xb0]:
                text_obj_addr = string_addr - m_text_offset

                # Validate by checking if this looks like a Text object
                # We can't easily validate without knowing more structure, but let's try
                # reading the area and looking for typical object patterns

                try:
                    # Read 256 bytes starting from potential Text object
                    obj_data = mem.read(text_obj_addr, 256)

                    # Check if the version string is at the expected offset
                    expected_string_offset = m_text_offset
                    if obj_data[expected_string_offset:expected_string_offset + len(version_pattern)] == version_pattern:
                        print(f"    ✓ Potential Text object at {hex(text_obj_addr)}")
                        print(f"      m_Text field at offset +{hex(m_text_offset)}")

                        # Show first 64 bytes of the object
                        print(f"      First 64 bytes:")
                        for j in range(0, min(64, len(obj_data)), 16):
                            hex_str = ' '.join(f'{b:02x}' for b in obj_data[j:j+16])
                            print(f"        {hex(text_obj_addr + j):016x}: {hex_str}")

                        print()

                        # This is likely the Text object!
                        return True
                except:
                    pass

            print()

        print("✗ Could not identify Text object structure")
        return False

    finally:
        scanner.close()

if __name__ == "__main__":
    success = find_text_with_raw_string()
    sys.exit(0 if success else 1)

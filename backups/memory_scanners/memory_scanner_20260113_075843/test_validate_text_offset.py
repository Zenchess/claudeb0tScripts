#!/usr/bin/env python3
"""Validate which offset is correct for Text.m_Text by checking object structure"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def validate_text_offsets():
    print("=" * 70)
    print("Validating Text object candidates")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Known location of version string
        version_string_addr = 0x7f1601d93c44

        # Test offsets for m_Text field
        test_offsets = [
            (0xd0, "CLAUDE.md reference"),
            (0xc8, "alternate 1"),
            (0xd8, "alternate 2"),
            (0xe0, "alternate 3"),
            (0xb8, "alternate 4"),
            (0xc0, "alternate 5"),
            (0xa8, "alternate 6"),
            (0xb0, "alternate 7"),
        ]

        print("Testing each candidate Text object:\n")

        for m_text_offset, desc in test_offsets:
            text_obj_addr = version_string_addr - m_text_offset

            print(f"[{desc}] Testing m_Text at +{hex(m_text_offset)}")
            print(f"    Text object would be at: {hex(text_obj_addr)}")

            try:
                # Read 512 bytes of the object
                obj_data = mem.read(text_obj_addr, 512)

                # Verify version string is at the expected offset
                version_pattern = b'v\x002\x00.\x000\x001\x006\x00'
                if obj_data[m_text_offset:m_text_offset + len(version_pattern)] != version_pattern:
                    print(f"    ✗ Version string not at offset +{hex(m_text_offset)}")
                    print()
                    continue

                print(f"    ✓ Version string confirmed at +{hex(m_text_offset)}")

                # Check for vtable pointer at +0x0 (first 8 bytes should be a valid pointer)
                vtable_ptr = struct.unpack('<Q', obj_data[0:8])[0]
                if vtable_ptr > 0x1000 and vtable_ptr < 0x7fffffffffff:
                    print(f"    ✓ Valid vtable pointer at +0x0: {hex(vtable_ptr)}")

                    # Try to read the vtable
                    try:
                        vtable_data = mem.read(vtable_ptr, 64)
                        print(f"      First 32 bytes of vtable: {vtable_data[:32].hex()}")
                    except:
                        print(f"      (Could not read vtable)")
                else:
                    print(f"    ✗ Invalid vtable pointer: {hex(vtable_ptr)}")

                # Show first 128 bytes of object in hex
                print(f"    First 128 bytes of object:")
                for i in range(0, 128, 16):
                    hex_str = ' '.join(f'{b:02x}' for b in obj_data[i:i+16])
                    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in obj_data[i:i+16])
                    print(f"      +{i:03x}: {hex_str}  {ascii_str}")

                # Check for other MonoObject/Unity Object fields
                # MonoObject typically has:
                # +0x0: vtable pointer
                # +0x8: MonoClass pointer or other metadata

                mono_class_ptr = struct.unpack('<Q', obj_data[8:16])[0]
                if mono_class_ptr > 0x1000 and mono_class_ptr < 0x7fffffffffff:
                    print(f"    ✓ Potential MonoClass at +0x8: {hex(mono_class_ptr)}")
                else:
                    print(f"    ⚠ Unusual value at +0x8: {hex(mono_class_ptr)}")

                print()

            except Exception as e:
                print(f"    ✗ Error reading object: {e}")
                print()
                continue

        print("=" * 70)
        print("Analysis complete")
        print("=" * 70)

    finally:
        scanner.close()

if __name__ == "__main__":
    validate_text_offsets()

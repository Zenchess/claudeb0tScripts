#!/usr/bin/env python3
"""Analyze memory around 'version' strings to identify object structures"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def analyze_version_objects():
    print("=" * 70)
    print("Analyzing objects with name 'version'")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Known 'version' string addresses from previous search
        version_strings = [
            (0x2b7cd67c, "ASCII"),
            (0x7f15d000cc1c, "ASCII"),
            (0x7f1639e08059, "ASCII"),
            (0x7f163a205079, "ASCII"),
            (0x7f163a605251, "ASCII"),
            (0x7f163a698584, "UTF-16"),  # This one looks promising
        ]

        print("Analyzing memory around each 'version' string:\n")

        for string_addr, string_type in version_strings:
            print(f"[{string_type}] String at {hex(string_addr)}")

            try:
                # Read 512 bytes before and after the string
                context_size = 512
                context_start = max(0, string_addr - context_size)
                context_data = mem.read(context_start, context_size * 2)

                # Calculate offset of string within context
                string_offset = string_addr - context_start

                # Display memory context
                print(f"  Memory context (±{context_size} bytes):")

                # Show 128 bytes before string
                print(f"\n  128 bytes BEFORE string:")
                start_show = max(0, string_offset - 128)
                for i in range(start_show, string_offset, 16):
                    if i + 16 <= len(context_data):
                        hex_str = ' '.join(f'{b:02x}' for b in context_data[i:i+16])
                        addr = context_start + i
                        print(f"    {addr:016x}: {hex_str}")

                # Show the string itself
                print(f"\n  → STRING at {hex(string_addr)}:")
                string_start = string_offset
                string_end = min(string_offset + 32, len(context_data))
                for i in range(string_start, string_end, 16):
                    if i + 16 <= len(context_data):
                        hex_str = ' '.join(f'{b:02x}' for b in context_data[i:i+16])
                        addr = context_start + i
                        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context_data[i:i+16])
                        print(f"    {addr:016x}: {hex_str}  {ascii_str}")

                # Show 128 bytes after string
                print(f"\n  128 bytes AFTER string:")
                after_start = string_offset + 16
                after_end = min(string_offset + 144, len(context_data))
                for i in range(after_start, after_end, 16):
                    if i + 16 <= len(context_data):
                        hex_str = ' '.join(f'{b:02x}' for b in context_data[i:i+16])
                        addr = context_start + i
                        print(f"    {addr:016x}: {hex_str}")

                # Look for potential object structures
                print(f"\n  Potential object structure analysis:")

                # Check for vtable-like pointers (at various offsets before the string)
                for test_offset in [0x18, 0x20, 0x28, 0x30, 0x10, 0x40]:
                    if string_offset >= test_offset + 8:
                        obj_base = string_offset - test_offset
                        if obj_base + 8 <= len(context_data):
                            vtable = struct.unpack('<Q', context_data[obj_base:obj_base+8])[0]
                            if 0x1000 < vtable < 0x7fffffffffff:
                                obj_addr = context_start + obj_base
                                print(f"    If name at +{hex(test_offset)}: Object at {hex(obj_addr)}, vtable {hex(vtable)}")

                print()
                print("-" * 70)
                print()

            except Exception as e:
                print(f"  ✗ Error reading memory: {e}")
                print()

        print("=" * 70)
        print("Analysis complete")
        print("=" * 70)

    finally:
        scanner.close()

if __name__ == "__main__":
    analyze_version_objects()

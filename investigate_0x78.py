#!/usr/bin/env python3
"""Investigate what's at offset +0x78"""
import sys
import struct
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Get shell window
window_data = scanner._windows_cache.get('shell')
if not window_data:
    print("shell window not found")
    sys.exit(1)

window_addr, tmp_addr = window_data

print(f"Shell window at: 0x{window_addr:x}")

# Read pointer at +0x78
ptr_data = scanner.memory_reader.read(window_addr + 0x78, 8)
ptr_value = struct.unpack('<Q', ptr_data)[0]

print(f"+0x78 pointer: 0x{ptr_value:x}")

if ptr_value != 0:
    # Try to read the object at this pointer
    # Check if it looks like a Dictionary (has capacity, count, etc.)
    print(f"\nReading object at 0x{ptr_value:x}:")

    # Dictionary structure typically has:
    # vtable ptr, type info, then fields like buckets, entries, count, etc.
    for offset in range(0x10, 0x30, 8):
        try:
            data = scanner.memory_reader.read(ptr_value + offset, 8)
            value = struct.unpack('<Q', data)[0]
            print(f"  +0x{offset:02x}: 0x{value:x}")

            # If it looks like a pointer, try to check if it's an array
            if 0x7f0000000000 < value < 0x800000000000:
                # Read potential array length
                try:
                    len_data = scanner.memory_reader.read(value + 0x18, 4)
                    length = struct.unpack('<i', len_data)[0]
                    if 0 < length < 10000:
                        print(f"      -> points to array with length: {length}")
                except:
                    pass
        except:
            break

# Also read +0x80 for comparison (output field)
print(f"\n+0x80 (output field):")
output_ptr_data = scanner.memory_reader.read(window_addr + 0x80, 8)
output_ptr = struct.unpack('<Q', output_ptr_data)[0]
print(f"  Pointer: 0x{output_ptr:x}")

if output_ptr != 0:
    print(f"  Object at +0x80 exists (NMOPNOICKDJ instance)")

    # Check if it has a Queue field at +0x10
    queue_ptr_data = scanner.memory_reader.read(output_ptr + 0x10, 8)
    queue_ptr = struct.unpack('<Q', queue_ptr_data)[0]
    print(f"  +0x10 (potential Queue): 0x{queue_ptr:x}")

#!/usr/bin/env python3
"""Try reading +0x78 as Queue with corrected offsets (head at +0x20)"""
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

if ptr_value == 0:
    print("NULL pointer")
    sys.exit(0)

# Try to read it as a Queue<string> with dunce's offsets
# Queue<T> structure:
#   T[] _array;    // +0x10
#   ??? field      // +0x18
#   int _head;     // +0x20  <- dunce says here
#   int _size;     // +0x24?

print("\nReading as Queue with head at +0x20:")

# Read array pointer
array_ptr_data = scanner.memory_reader.read(ptr_value + 0x10, 8)
array_ptr = struct.unpack('<Q', array_ptr_data)[0]
print(f"  _array (+0x10): 0x{array_ptr:x}")

# What's at +0x18?
field_18_data = scanner.memory_reader.read(ptr_value + 0x18, 4)
field_18 = struct.unpack('<i', field_18_data)[0]
print(f"  unknown (+0x18): {field_18}")

# Read head at +0x20
head_data = scanner.memory_reader.read(ptr_value + 0x20, 4)
head = struct.unpack('<i', head_data)[0]
print(f"  _head (+0x20): {head}")

# Try size at various offsets
for size_offset in [0x24, 0x28, 0x2c]:
    size_data = scanner.memory_reader.read(ptr_value + size_offset, 4)
    size = struct.unpack('<i', size_data)[0]
    print(f"  possible _size (+0x{size_offset:x}): {size}")

if array_ptr != 0:
    # Read Mono array length (at array + 0x18)
    try:
        len_data = scanner.memory_reader.read(array_ptr + 0x18, 4)
        capacity = struct.unpack('<i', len_data)[0]
        print(f"  array capacity: {capacity}")

        # Try different size offsets
        for size_offset in [0x24, 0x28]:
            size_data = scanner.memory_reader.read(ptr_value + size_offset, 4)
            size = struct.unpack('<i', size_data)[0]

            if 0 < size < 1000 and 0 <= head < capacity:
                print(f"\n  Trying with head={head}, size={size} (from +0x{size_offset:x}):")
                read_count = min(size, 5, capacity)

                for i in range(read_count):
                    slot = (head + i) % capacity
                    element_addr = array_ptr + 0x20 + (slot * 8)
                    elem_ptr_data = scanner.memory_reader.read(element_addr, 8)
                    elem_ptr = struct.unpack('<Q', elem_ptr_data)[0]

                    if elem_ptr != 0:
                        string_val = scanner._read_mono_string(elem_ptr)
                        if string_val:
                            print(f"    [{i}]: {string_val[:100]}")
    except Exception as e:
        print(f"  Error: {e}")

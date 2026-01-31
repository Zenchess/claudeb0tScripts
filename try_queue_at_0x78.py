#!/usr/bin/env python3
"""Try reading +0x78 as a Queue<string> directly"""
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

# Try to read it as a Queue<string>
# Queue<T> structure:
#   T[] _array;    // +0x10
#   int _head;     // +0x18
#   int _size;     // +0x20 (but could be +0x1c)
#   int _version;  // +0x24 (or +0x20)

print("\nTrying to read as Queue<string>:")

# Read array pointer
array_ptr_data = scanner.memory_reader.read(ptr_value + 0x10, 8)
array_ptr = struct.unpack('<Q', array_ptr_data)[0]
print(f"  _array (+0x10): 0x{array_ptr:x}")

# Try head at +0x18
head_data = scanner.memory_reader.read(ptr_value + 0x18, 4)
head = struct.unpack('<i', head_data)[0]
print(f"  _head (+0x18): {head}")

# Try size at +0x1c
size_1c_data = scanner.memory_reader.read(ptr_value + 0x1c, 4)
size_1c = struct.unpack('<i', size_1c_data)[0]
print(f"  possible _size (+0x1c): {size_1c}")

# Try size at +0x20
size_20_data = scanner.memory_reader.read(ptr_value + 0x20, 4)
size_20 = struct.unpack('<i', size_20_data)[0]
print(f"  possible _size (+0x20): {size_20}")

if array_ptr != 0:
    # Try to read array length
    try:
        len_data = scanner.memory_reader.read(array_ptr + 0x18, 4)
        capacity = struct.unpack('<i', len_data)[0]
        print(f"  array capacity: {capacity}")

        # If size looks reasonable, try to read some strings
        for size_offset, size_val in [(0x1c, size_1c), (0x20, size_20)]:
            if 0 < size_val < 1000:
                print(f"\n  Trying with size={size_val} from +0x{size_offset:x}:")
                read_count = min(size_val, 5, capacity)

                for i in range(read_count):
                    slot = (head + i) % capacity
                    element_addr = array_ptr + 0x20 + (slot * 8)
                    elem_ptr_data = scanner.memory_reader.read(element_addr, 8)
                    elem_ptr = struct.unpack('<Q', elem_ptr_data)[0]

                    if elem_ptr != 0:
                        # Try to read as MonoString
                        string_val = scanner._read_mono_string(elem_ptr)
                        if string_val:
                            print(f"    [{i}]: {string_val[:80]}")
    except Exception as e:
        print(f"  Error reading array: {e}")

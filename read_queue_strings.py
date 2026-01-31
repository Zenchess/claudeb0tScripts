#!/usr/bin/env python3
"""Read strings from NMOPNOICKDJ Queue"""
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

# Read NMOPNOICKDJ -> Queue chain
nmop_ptr_data = scanner.memory_reader.read(window_addr + 0x78, 8)
nmop_ptr = struct.unpack('<Q', nmop_ptr_data)[0]

queue_ptr_data = scanner.memory_reader.read(nmop_ptr + 0x10, 8)
queue_ptr = struct.unpack('<Q', queue_ptr_data)[0]

# Read Queue fields
array_ptr_data = scanner.memory_reader.read(queue_ptr + 0x10, 8)
array_ptr = struct.unpack('<Q', array_ptr_data)[0]

head_data = scanner.memory_reader.read(queue_ptr + 0x20, 4)
head = struct.unpack('<i', head_data)[0]

size_data = scanner.memory_reader.read(queue_ptr + 0x28, 4)
size = struct.unpack('<i', size_data)[0]

print(f"Queue has {size} elements, head={head}")

# Read array capacity
cap_data = scanner.memory_reader.read(array_ptr + 0x18, 4)
capacity = struct.unpack('<i', cap_data)[0]

print(f"Array capacity: {capacity}")

# Read last 10 strings
print(f"\nLast 10 strings:")
read_count = min(10, size)
for i in range(size - read_count, size):
    slot = (head + i) % capacity
    elem_addr = array_ptr + 0x20 + (slot * 8)
    elem_ptr_data = scanner.memory_reader.read(elem_addr, 8)
    elem_ptr = struct.unpack('<Q', elem_ptr_data)[0]

    if elem_ptr != 0:
        string_val = scanner._read_mono_string(elem_ptr)
        if string_val:
            # Truncate long strings
            display = string_val[:100] + "..." if len(string_val) > 100 else string_val
            print(f"  [{i}]: {display}")

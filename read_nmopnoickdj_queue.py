#!/usr/bin/env python3
"""Read Queue from NMOPNOICKDJ at Window+0x78"""
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

# Read NMOPNOICKDJ pointer at +0x78
nmop_ptr_data = scanner.memory_reader.read(window_addr + 0x78, 8)
nmop_ptr = struct.unpack('<Q', nmop_ptr_data)[0]

print(f"NMOPNOICKDJ at +0x78: 0x{nmop_ptr:x}")

if nmop_ptr == 0:
    print("NULL - trying +0x80 instead...")
    # Try reading from +0x80 (output field)
    nmop_ptr_data = scanner.memory_reader.read(window_addr + 0x80, 8)
    nmop_ptr = struct.unpack('<Q', nmop_ptr_data)[0]
    print(f"NMOPNOICKDJ at +0x80: 0x{nmop_ptr:x}")

if nmop_ptr == 0:
    print("Both offsets are NULL!")
    sys.exit(1)

# NMOPNOICKDJ.FFAKOMDAHHC is the first field, at +0x10
queue_ptr_data = scanner.memory_reader.read(nmop_ptr + 0x10, 8)
queue_ptr = struct.unpack('<Q', queue_ptr_data)[0]

print(f"Queue<string> FFAKOMDAHHC at +0x10: 0x{queue_ptr:x}")

if queue_ptr == 0:
    print("Queue pointer is NULL!")
    sys.exit(1)

# Read Queue fields (array:0x10, head:0x20, size:0x28)
array_ptr_data = scanner.memory_reader.read(queue_ptr + 0x10, 8)
array_ptr = struct.unpack('<Q', array_ptr_data)[0]

head_data = scanner.memory_reader.read(queue_ptr + 0x20, 4)
head = struct.unpack('<i', head_data)[0]

size_data = scanner.memory_reader.read(queue_ptr + 0x28, 4)
size = struct.unpack('<i', size_data)[0]

print(f"\nQueue structure:")
print(f"  array: 0x{array_ptr:x}")
print(f"  head: {head}")
print(f"  size: {size}")

if size == 0:
    print("\n❌ Queue is empty")
else:
    print(f"\n✅ Queue has {size} elements!")

#!/usr/bin/env python3
"""Read Queue with correct offsets from dunce: array:0x10, head:0x20, size:0x28"""
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
queue_ptr = struct.unpack('<Q', ptr_data)[0]

print(f"+0x78 Queue pointer: 0x{queue_ptr:x}")

if queue_ptr == 0:
    print("NULL pointer")
    sys.exit(0)

# Read Queue fields with dunce's offsets
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
    print("\n❌ Queue is empty (size=0)")
else:
    print(f"\n✅ Queue has {size} elements!")

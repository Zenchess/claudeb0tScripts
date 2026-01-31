#!/usr/bin/env python3
"""Check Mono array structure"""
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

# Read pointer at +0x78
ptr_data = scanner.memory_reader.read(window_addr + 0x78, 8)
dict_ptr = struct.unpack('<Q', ptr_data)[0]

# Read array pointer from Dictionary/Queue
array_ptr_data = scanner.memory_reader.read(dict_ptr + 0x10, 8)
array_ptr = struct.unpack('<Q', array_ptr_data)[0]

print(f"Array at: 0x{array_ptr:x}")
print("\nMono array structure scan:")

# Scan for the length field
for offset in range(0x8, 0x20, 4):
    data = scanner.memory_reader.read(array_ptr + offset, 4)
    value = struct.unpack('<i', data)[0]
    print(f"  +0x{offset:02x}: {value}")

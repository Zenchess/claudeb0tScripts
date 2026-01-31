#!/usr/bin/env python3
"""Check Queue at +0x78 for all windows"""
import sys
import struct
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Check multiple windows
for window_name in ['shell', 'chat', 'badge', 'breach']:
    window_data = scanner._windows_cache.get(window_name)
    if not window_data:
        print(f"{window_name}: not in cache")
        continue

    window_addr, tmp_addr = window_data

    # Read pointer at +0x78
    try:
        ptr_data = scanner.memory_reader.read(window_addr + 0x78, 8)
        queue_ptr = struct.unpack('<Q', ptr_data)[0]

        if queue_ptr == 0:
            print(f"{window_name}: +0x78 is NULL")
            continue

        # Read Queue fields
        array_ptr_data = scanner.memory_reader.read(queue_ptr + 0x10, 8)
        array_ptr = struct.unpack('<Q', array_ptr_data)[0]

        head_data = scanner.memory_reader.read(queue_ptr + 0x20, 4)
        head = struct.unpack('<i', head_data)[0]

        size_data = scanner.memory_reader.read(queue_ptr + 0x28, 4)
        size = struct.unpack('<i', size_data)[0]

        print(f"{window_name}: array=0x{array_ptr:x}, head={head}, size={size}")
    except Exception as e:
        print(f"{window_name}: error - {e}")

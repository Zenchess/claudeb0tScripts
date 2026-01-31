#!/usr/bin/env python3
"""Scan Window memory for any populated Queue<string>"""
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
print(f"\nScanning from +0x0 to +0x200 for populated Queues...")

# Scan every 8-byte aligned offset
for offset in range(0, 0x200, 8):
    try:
        # Read potential queue pointer
        ptr_data = scanner.memory_reader.read(window_addr + offset, 8)
        queue_ptr = struct.unpack('<Q', ptr_data)[0]

        # Skip NULL and invalid pointers
        if queue_ptr == 0 or queue_ptr < 0x7f0000000000 or queue_ptr > 0x800000000000:
            continue

        # Try to read as Queue structure
        try:
            array_ptr_data = scanner.memory_reader.read(queue_ptr + 0x10, 8)
            array_ptr = struct.unpack('<Q', array_ptr_data)[0]

            head_data = scanner.memory_reader.read(queue_ptr + 0x20, 4)
            head = struct.unpack('<i', head_data)[0]

            size_data = scanner.memory_reader.read(queue_ptr + 0x28, 4)
            size = struct.unpack('<i', size_data)[0]

            # Check if this looks like a valid Queue with data
            if 0 < size < 10000 and 0 <= head < 10000:
                print(f"\n✅ FOUND at +0x{offset:02x}:")
                print(f"   Queue ptr: 0x{queue_ptr:x}")
                print(f"   array: 0x{array_ptr:x}")
                print(f"   head: {head}")
                print(f"   size: {size}")

                # Try to read first string
                if array_ptr != 0 and array_ptr > 0x7f0000000000:
                    try:
                        # Try to read array capacity
                        cap_data = scanner.memory_reader.read(array_ptr + 0x18, 4)
                        capacity = struct.unpack('<i', cap_data)[0]

                        if capacity > 0:
                            # Try to read first element
                            slot = head % capacity
                            elem_addr = array_ptr + 0x20 + (slot * 8)
                            elem_ptr_data = scanner.memory_reader.read(elem_addr, 8)
                            elem_ptr = struct.unpack('<Q', elem_ptr_data)[0]

                            if elem_ptr != 0:
                                string_val = scanner._read_mono_string(elem_ptr)
                                if string_val:
                                    print(f"   First string: {string_val[:80]}")
                    except:
                        pass
        except:
            pass
    except:
        pass

print("\nDone scanning.")

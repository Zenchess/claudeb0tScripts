#!/usr/bin/env python3
"""Dump memory area around expected char_width/char_height location"""
import sys
import struct
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Get shell window address
window_data = scanner._windows_cache.get('shell')
if not window_data:
    print("shell window not found")
    sys.exit(1)

window_addr, tmp_addr = window_data

# Dump from +0x90 to +0xb0 (around wrapped_output, scroll_offset, char_height, char_width)
print(f"Shell window at: 0x{window_addr:x}")
print(f"\nMemory dump from +0x90 to +0xb0:")
for offset in range(0x90, 0xb0, 4):
    data = scanner.memory_reader.read(window_addr + offset, 4)
    value_int = struct.unpack('<i', data)[0]
    value_hex = struct.unpack('<I', data)[0]
    print(f"  +0x{offset:02x}: {value_int:10d} (0x{value_hex:08x})")

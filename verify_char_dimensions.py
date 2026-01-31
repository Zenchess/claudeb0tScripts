#!/usr/bin/env python3
"""Verify char_width and char_height at +0xd8"""
import sys
import struct
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Confirmed offsets
CHAR_HEIGHT_OFFSET = 0xd8
CHAR_WIDTH_OFFSET = 0xdc

for window_name in ['shell', 'chat']:
    window_data = scanner._windows_cache.get(window_name)
    if not window_data:
        continue

    window_addr, tmp_addr = window_data

    char_height_data = scanner.memory_reader.read(window_addr + CHAR_HEIGHT_OFFSET, 4)
    char_width_data = scanner.memory_reader.read(window_addr + CHAR_WIDTH_OFFSET, 4)

    char_height = struct.unpack('<i', char_height_data)[0]
    char_width = struct.unpack('<i', char_width_data)[0]

    print(f"{window_name}: char_height={char_height}, char_width={char_width}")

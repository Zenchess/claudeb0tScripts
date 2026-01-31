#!/usr/bin/env python3
"""Read char_width and char_height from Window instances"""
import sys
import struct
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Field offsets based on Window class layout
# After output (+0x80), edit_output (+0x88), wrapped_output (+0x90), scroll_offset (+0x98):
CHAR_HEIGHT_OFFSET = 0x9c
CHAR_WIDTH_OFFSET = 0xa0

# Get window addresses from scanner's cache
for window_name in ['shell', 'chat']:
    window_data = scanner._windows_cache.get(window_name)
    if not window_data:
        print(f"{window_name}: not found in cache")
        continue

    window_addr, tmp_addr = window_data

    # Read char_height and char_width
    try:
        char_height_data = scanner.memory_reader.read(window_addr + CHAR_HEIGHT_OFFSET, 4)
        char_width_data = scanner.memory_reader.read(window_addr + CHAR_WIDTH_OFFSET, 4)

        char_height = struct.unpack('<i', char_height_data)[0]
        char_width = struct.unpack('<i', char_width_data)[0]

        print(f"{window_name}: char_width={char_width}, char_height={char_height}")
    except Exception as e:
        print(f"{window_name}: error reading dimensions - {e}")

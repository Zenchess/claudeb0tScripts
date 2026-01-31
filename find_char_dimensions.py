#!/usr/bin/env python3
"""Scan for char_width and char_height by finding reasonable consecutive int pairs"""
import sys
import struct
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Get shell and chat window addresses
for window_name in ['shell', 'chat']:
    window_data = scanner._windows_cache.get(window_name)
    if not window_data:
        print(f"{window_name}: not found")
        continue

    window_addr, tmp_addr = window_data
    print(f"\n{window_name} window at: 0x{window_addr:x}")

    # Scan from +0x80 to +0x150 looking for pairs of reasonable dimensions
    print(f"Scanning for dimension pairs (both 30-300):")
    for offset in range(0x80, 0x150, 4):
        try:
            data1 = scanner.memory_reader.read(window_addr + offset, 4)
            data2 = scanner.memory_reader.read(window_addr + offset + 4, 4)

            val1 = struct.unpack('<i', data1)[0]
            val2 = struct.unpack('<i', data2)[0]

            # Look for pairs of reasonable dimension values
            if 30 < val1 < 300 and 30 < val2 < 300:
                print(f"  +0x{offset:02x}: {val1}, {val2} <-- CANDIDATE")
        except:
            pass

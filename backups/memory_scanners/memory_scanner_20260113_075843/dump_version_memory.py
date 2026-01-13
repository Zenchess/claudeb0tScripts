#!/usr/bin/env python3
"""Dump memory around version string to understand structure"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()
mem = scanner.memory_reader

# Known version string address
version_addr = 0x7f1601d93c44

# Dump 256 bytes before and after
start = version_addr - 256
size = 512

print(f"Dumping memory around version string at {hex(version_addr)}")
print(f"Range: {hex(start)} - {hex(start + size)}")
print()

data = mem.read(start, size)

# Print as hex dump
for i in range(0, len(data), 16):
    addr = start + i
    hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
    marker = ' <-- VERSION' if version_addr >= addr and version_addr < addr + 16 else ''
    print(f'{hex(addr)}: {hex_str:<48} {ascii_str}{marker}')

#!/usr/bin/env python3
"""Debug MonoString reading"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()
mem = scanner.memory_reader

# From memory dump:
# Length (06 00 00 00) at 0x7f1601d93c34
# Data (v2.016 UTF-16) at 0x7f1601d93c44

length_addr = 0x7f1601d93c34
data_addr = 0x7f1601d93c44

# If length is at +0x10 in MonoString:
# MonoString base = length_addr - 0x10
monostring_base = length_addr - 0x10

print(f"Length address: {hex(length_addr)}")
print(f"Data address: {hex(data_addr)}")
print(f"Calculated MonoString base: {hex(monostring_base)}")
print()

# Data offset from base
data_offset = data_addr - monostring_base
print(f"Data offset from base: {hex(data_offset)}")
print()

# Try to read length
try:
    length = mem.read_uint32(monostring_base + 0x10)
    print(f"Length at base+0x10: {length}")
except Exception as e:
    print(f"Error reading length: {e}")

# Try to read data
try:
    data = mem.read(monostring_base + data_offset, 6 * 2)  # 6 chars, UTF-16
    text = data.decode('utf-16-le')
    print(f"Text at base+{hex(data_offset)}: '{text}'")
except Exception as e:
    print(f"Error reading text: {e}")

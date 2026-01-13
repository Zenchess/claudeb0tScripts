#!/usr/bin/env python3
"""Find all references to the version MonoString in memory"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()
mem = scanner.memory_reader

# Known MonoString address from previous run
monostring_addr = 0x7f1601d93c38
ptr_bytes = struct.pack('<Q', monostring_addr)

print(f"Searching for pointers to MonoString at {hex(monostring_addr)}")
print()

# Get memory regions
maps_file = f"/proc/{scanner.pid}/maps"
regions = []
with open(maps_file, 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2 and 'rw' in parts[1]:
            addr_range = parts[0]
            start, end = addr_range.split('-')
            regions.append((int(start, 16), int(end, 16)))

print(f"Scanning {len(regions)} memory regions...")
print()

# Search for the pointer
found_count = 0
for start, end in regions:
    try:
        chunk_size = 1024 * 1024
        for offset in range(0, end - start, chunk_size):
            addr = start + offset
            read_size = min(chunk_size, end - addr)

            try:
                data = mem.read(addr, read_size)
                pos = 0
                while True:
                    pos = data.find(ptr_bytes, pos)
                    if pos == -1:
                        break

                    ptr_addr = addr + pos
                    found_count += 1

                    # Show first 10 matches
                    if found_count <= 10:
                        print(f"[{found_count}] Found pointer at {hex(ptr_addr)}")

                        # Show what offsets this could be
                        for name, offset in [("Text.m_Text", 0xd0), ("Text.m_text", 0xc8), ("some_field", 0x40)]:
                            obj_addr = ptr_addr - offset
                            print(f"    If this is {name} (+{hex(offset)}), object is at {hex(obj_addr)}")
                        print()

                    pos += 1
            except:
                pass
    except:
        pass

print(f"Total pointers found: {found_count}")

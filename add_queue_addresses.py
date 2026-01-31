#!/usr/bin/env python3
"""Add Queue addresses to mono_addresses.json"""
import sys
import json
import struct
from pathlib import Path

sys.path.insert(0, 'python_lib')
from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Read current mono_addresses.json
addresses_file = Path('data/mono_addresses.json')
with open(addresses_file) as f:
    addresses = json.load(f)

# For each window, read Queue address
for window_name, data in addresses['windows'].items():
    window_addr = int(data['window_addr'], 16)

    # Read NMOPNOICKDJ pointer at Window +0x78
    nmop_ptr_data = scanner.memory_reader.read(window_addr + 0x78, 8)
    nmop_ptr = struct.unpack('<Q', nmop_ptr_data)[0]

    if nmop_ptr != 0:
        # Read Queue pointer at NMOPNOICKDJ +0x10
        queue_ptr_data = scanner.memory_reader.read(nmop_ptr + 0x10, 8)
        queue_ptr = struct.unpack('<Q', queue_ptr_data)[0]

        # Add to data
        data['queue_addr'] = f"0x{queue_ptr:x}"
        print(f"{window_name}: queue_addr = {data['queue_addr']}")
    else:
        print(f"{window_name}: NMOPNOICKDJ is NULL")

# Save updated addresses
with open(addresses_file, 'w') as f:
    json.dump(addresses, f, indent=2)

print(f"\nUpdated {addresses_file}")

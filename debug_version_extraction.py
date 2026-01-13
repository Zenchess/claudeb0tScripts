#!/usr/bin/env python3
"""Debug version string extraction"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def debug_extraction():
    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Pattern for version string
        version_prefix = b'v\x002\x00.\x00'

        regions = scanner._get_memory_regions()

        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:
                continue

            try:
                data = mem.read(start, size)
                pos = data.find(version_prefix)
                if pos == -1:
                    continue

                # Found it!
                print(f"Found version prefix at {hex(start + pos)}")
                print()

                # Extract more context
                context_start = pos
                context_end = min(pos + 64, len(data))
                context = data[context_start:context_end]

                print(f"Raw bytes (hex): {context.hex()}")
                print()

                # Decode
                decoded = context.decode('utf-16le', errors='ignore')
                print(f"Decoded UTF-16: {repr(decoded)}")
                print()

                # Show character by character
                print("Character analysis:")
                for i, char in enumerate(decoded[:20]):
                    print(f"  [{i}] {repr(char)} (ord={ord(char)}, printable={char.isprintable()})")

                break

            except:
                continue

    finally:
        scanner.close()

if __name__ == "__main__":
    debug_extraction()

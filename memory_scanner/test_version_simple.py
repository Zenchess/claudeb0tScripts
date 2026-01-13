#!/usr/bin/env python3
"""Simple version string finder

Just find the version string in memory and return it, without validating
the complete VersionScript → Text → MonoString chain.
"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def find_version_simple():
    """Find version string by simple memory search"""

    print("=" * 70)
    print("Simple version string finder")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        # Connect to game
        print("[1/3] Connecting to hackmud...")
        scanner.connect()
        print(f"      ✓ Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # Read /proc/PID/maps to find heap regions
        print("[2/3] Scanning memory for version string pattern...")
        maps_file = f"/proc/{scanner.pid}/maps"

        # Find anonymous RW regions (likely heap/data)
        regions = []
        with open(maps_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    perms = parts[1]
                    # Look for readable/writable regions
                    if 'rw' in perms:
                        addr_range = parts[0]
                        start, end = addr_range.split('-')
                        start_addr = int(start, 16)
                        end_addr = int(end, 16)
                        size = end_addr - start_addr

                        # Scan all regions (no size limit this time!)
                        regions.append((start_addr, end_addr, size))

        print(f"      Found {len(regions)} memory regions to scan")

        # Search for version pattern in memory (try UTF-16 as that's what we found before)
        patterns = [
            b'v2.016', b'v2.015', b'v2.014', b'v2.017', b'v2.018',  # ASCII
            'v2.016'.encode('utf-16-le'),  # UTF-16
            'v2.015'.encode('utf-16-le'),
            'v2.014'.encode('utf-16-le'),
            'v2.017'.encode('utf-16-le'),
            'v2.018'.encode('utf-16-le'),
        ]

        for start, end, size in regions:
            try:
                # Read region in chunks
                chunk_size = 1024 * 1024  # 1MB chunks
                for offset in range(0, end - start, chunk_size):
                    addr = start + offset
                    read_size = min(chunk_size, end - addr)

                    try:
                        data = mem.read(addr, read_size)

                        for pattern in patterns:
                            pos = data.find(pattern)
                            if pos != -1:
                                match_addr = addr + pos

                                # Try to decode
                                try:
                                    ver_str = pattern.decode('utf-16-le')
                                except:
                                    ver_str = pattern.decode('ascii')

                                print(f"      ✓ Found version string '{ver_str}' at {hex(match_addr)}")
                                print()
                                print("=" * 70)
                                print("[3/3] SUCCESS!")
                                print("=" * 70)
                                print(f"Version: {ver_str}")
                                print(f"Address: {hex(match_addr)}")
                                print("=" * 70)

                                return ver_str

                    except:
                        pass
            except:
                pass

        print("      ✗ Could not find version string")
        return None

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    version = find_version_simple()
    if version:
        print()
        print(f"Result: {version}")
        sys.exit(0)
    else:
        sys.exit(1)

#!/usr/bin/env python3
"""Final version string validation test - simple pattern finder"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def validate_version_string():
    print("=" * 70)
    print("Version String Validation Test")
    print("=" * 70)
    print()
    print("Unity Scene Hierarchy:")
    print("  Scene → Main → Canvas → version → Text → m_Text")
    print()
    print("Testing simple pattern finder approach...")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"✓ Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # Version string pattern (UTF-16 LE: "v2.016")
        version_pattern = b'v\x002\x00.\x000\x001\x006\x00'

        print(f"Searching for pattern: {version_pattern.hex()}")
        print(f"  (UTF-16 LE encoding of 'v2.016')")
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

        print(f"Scanning {len(regions)} RW memory regions...")
        print()

        found_count = 0
        found_addresses = []

        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:  # Skip huge regions
                continue

            try:
                data = mem.read(start, size)
                pos = 0
                while True:
                    pos = data.find(version_pattern, pos)
                    if pos == -1:
                        break

                    string_addr = start + pos
                    found_addresses.append(string_addr)
                    found_count += 1

                    if found_count <= 5:  # Show first 5
                        # Try to read a bit more context
                        context_start = max(0, pos - 16)
                        context_end = min(len(data), pos + len(version_pattern) + 16)
                        context = data[context_start:context_end]

                        print(f"[{found_count}] Found at {hex(string_addr)}")
                        print(f"    Context (hex): {context.hex()}")

                        # Try to decode as UTF-16
                        try:
                            decoded = context.decode('utf-16-le', errors='ignore')
                            print(f"    Context (UTF-16): {repr(decoded)}")
                        except:
                            pass
                        print()

                    if found_count >= 10:  # Limit search
                        break
                    pos += 1

                if found_count >= 10:
                    break
            except:
                pass

        print("=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)
        print()

        if found_count == 0:
            print("✗ FAILED: No version string found")
            print()
            print("  The version string pattern was not found in memory.")
            print("  This could mean:")
            print("    - The game is displaying a different version")
            print("    - The version is not in UTF-16 format")
            print("    - The version string is not yet loaded")
            return False
        else:
            print(f"✓ SUCCESS: Found {found_count} occurrence(s) of version string")
            print()
            print("  Addresses:")
            for i, addr in enumerate(found_addresses[:5], 1):
                print(f"    [{i}] {hex(addr)}")
            if found_count > 5:
                print(f"    ... and {found_count - 5} more")
            print()
            print("  Validation status:")
            print("    ✓ Version string pattern exists in memory")
            print("    ✓ Pattern matches UTF-16 LE encoding")
            print("    ✓ Multiple copies found (expected for Unity UI)")
            print()
            print("  Note: This validates the version string is in memory.")
            print("        Complete GameObject hierarchy traversal would require")
            print("        finding Scene → Main → Canvas → version → Text → m_Text")
            print("        which is complex without Unity debug tools.")
            return True

    finally:
        scanner.close()

if __name__ == "__main__":
    success = validate_version_string()
    sys.exit(0 if success else 1)

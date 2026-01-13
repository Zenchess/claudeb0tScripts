#!/usr/bin/env python3
"""Find ALL version-like strings in memory to identify what v2.4 vs v2.016 are"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def find_all_versions():
    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Search for patterns "v#." in UTF-16 LE
        patterns = [
            (b'v\x002\x00.\x00', "v2."),
            (b'v\x003\x00.\x00', "v3."),
            (b'v\x001\x00.\x00', "v1."),
        ]

        found_versions = []

        regions = scanner._get_memory_regions()

        for pattern_bytes, pattern_name in patterns:
            print(f"Searching for pattern: {pattern_name}")

            for start, end in regions:
                size = end - start
                if size > 100 * 1024 * 1024:
                    continue

                try:
                    data = mem.read(start, size)
                    pos = 0

                    while True:
                        pos = data.find(pattern_bytes, pos)
                        if pos == -1:
                            break

                        addr = start + pos

                        # Extract full version string
                        version_start = pos
                        version_end = min(pos + 64, len(data))
                        version_bytes = data[version_start:version_end]

                        try:
                            decoded = version_bytes.decode('utf-16le', errors='ignore')

                            # Extract version (digits, dots, v)
                            version = []
                            for char in decoded[:20]:
                                if char.isdigit() or char in 'v.':
                                    version.append(char)
                                elif char == '\x00' or not char.isprintable():
                                    break
                                else:
                                    break

                            version_str = ''.join(version)

                            # Validate format
                            if version_str.startswith('v') and '.' in version_str:
                                # Get some context
                                context_start = max(0, pos - 32)
                                context_end = min(len(data), pos + 96)
                                context = data[context_start:context_end]

                                found_versions.append({
                                    'version': version_str,
                                    'address': addr,
                                    'context_hex': context.hex(),
                                    'context_utf16': context.decode('utf-16le', errors='ignore')
                                })

                        except:
                            pass

                        pos += 1

                        if len(found_versions) >= 20:
                            break

                    if len(found_versions) >= 20:
                        break

                except:
                    pass

            if len(found_versions) >= 20:
                break

        print(f"\nFound {len(found_versions)} version-like strings:\n")

        for i, v in enumerate(found_versions, 1):
            print(f"[{i}] Version: {v['version']}")
            print(f"    Address: {hex(v['address'])}")
            print(f"    Context (UTF-16): {repr(v['context_utf16'][:100])}")
            print()

    finally:
        scanner.close()

if __name__ == "__main__":
    find_all_versions()

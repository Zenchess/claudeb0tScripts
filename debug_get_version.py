#!/usr/bin/env python3
"""Debug what candidates get_version() finds"""

import sys
import re
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def debug_get_version():
    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader
        regions = scanner._get_memory_regions()

        candidates = []

        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:
                continue

            try:
                data = mem.read(start, size)

                version_prefix = b'v\x002\x00.\x00'
                pos = 0

                while True:
                    pos = data.find(version_prefix, pos)
                    if pos == -1:
                        break

                    version_start = pos
                    version_end = min(pos + 64, len(data))
                    version_bytes = data[version_start:version_end]

                    try:
                        decoded = version_bytes.decode('utf-16le', errors='ignore')

                        match = re.match(r'v(\d+)\.(\d+)', decoded)
                        if match:
                            version_str = match.group(0)
                            minor = match.group(2)

                            # Get context
                            context_start = max(0, pos - 64)
                            context_end = min(len(data), pos + 64)
                            context = data[context_start:context_end].decode('utf-16le', errors='ignore')

                            # Check for :::
                            has_triple_colon = ':::' in context

                            if len(minor) >= 2:
                                candidates.append({
                                    'version': version_str,
                                    'minor_len': len(minor),
                                    'address': hex(start + pos),
                                    'has_:::': has_triple_colon,
                                    'context': context[:60]
                                })

                    except UnicodeDecodeError:
                        pass

                    pos += 1

                    if len(candidates) >= 20:
                        break

            except:
                pass

            if len(candidates) >= 20:
                break

        print(f"Found {len(candidates)} candidates:\n")

        # Filter out ::: versions
        filtered = [c for c in candidates if not c['has_:::']]
        print(f"After filtering out ':::' versions: {len(filtered)}\n")

        for i, c in enumerate(filtered[:10], 1):
            print(f"[{i}] {c['version']} (minor_len={c['minor_len']})")
            print(f"    Address: {c['address']}")
            print(f"    Context: {repr(c['context'])}")
            print()

        # Sort by minor length
        filtered.sort(key=lambda x: x['minor_len'], reverse=True)
        if filtered:
            print(f"Winner: {filtered[0]['version']} (minor_len={filtered[0]['minor_len']})")

    finally:
        scanner.close()

if __name__ == "__main__":
    debug_get_version()

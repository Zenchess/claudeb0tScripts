#!/usr/bin/env python3
"""Debug trace of get_version() showing variable values at each step"""

import sys
import re
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def debug_get_version():
    print("=" * 80)
    print("DEBUG TRACE: get_version()")
    print("=" * 80)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"✓ Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # Step 1: Memory Region Enumeration
        print("[STEP 1] Memory Region Enumeration")
        regions = scanner._get_memory_regions()
        print(f"  regions = (list of {len(regions)} memory regions)")
        print(f"  First 3 regions:")
        for i, (start, end) in enumerate(regions[:3], 1):
            print(f"    [{i}] start={hex(start)}, end={hex(end)}, size={end-start:,} bytes")
        print()

        # Step 2-6: Pattern Search
        print("[STEP 2-6] Pattern Search Loop")
        candidates = []
        print(f"  candidates = [] (empty list)")
        print()

        version_found = False
        for region_idx, (start, end) in enumerate(regions):
            size = end - start
            if size > 100 * 1024 * 1024:
                continue

            try:
                data = mem.read(start, size)

                version_prefix = b'v\x00'
                pos = 0

                while True:
                    pos = data.find(version_prefix, pos)
                    if pos == -1:
                        break

                    # [STEP 2] Binary Pattern Search
                    if not version_found:
                        print(f"  [Region {region_idx}] Found 'v\\x00' at offset {pos} (absolute: {hex(start + pos)})")

                    # [STEP 3] UTF-16 Decoding
                    version_start = pos
                    version_end = min(pos + 64, len(data))
                    version_bytes = data[version_start:version_end]

                    try:
                        decoded = version_bytes.decode('utf-16le', errors='ignore')

                        if not version_found:
                            print(f"    version_bytes[:20] = {version_bytes[:20]}")
                            print(f"    decoded = {repr(decoded[:20])}")

                        # [STEP 4] Regex Version Extraction
                        match = re.match(r'v(\d+)\.(\d+)', decoded)
                        if match:
                            version_str = match.group(0)
                            minor = match.group(2)

                            if not version_found:
                                print(f"    match = {match}")
                                print(f"    version_str = {repr(version_str)}")
                                print(f"    minor = {repr(minor)}")

                            # [STEP 5] Context Filtering
                            context_start = max(0, pos - 64)
                            context_end = min(len(data), pos + 64)
                            context = data[context_start:context_end].decode('utf-16le', errors='ignore')

                            if not version_found:
                                print(f"    context (first 80 chars) = {repr(context[:80])}")

                            if ':::' in context:
                                if not version_found:
                                    print(f"    ✗ Filtered out (contains ':::')")
                                    print()
                                pos += 1
                                continue

                            if not version_found:
                                print(f"    ✓ Passed filter (no ':::')")

                            # Collect candidate
                            if len(minor) >= 2:
                                if not version_found:
                                    print(f"    ✓ Added to candidates: ({len(minor)}, {repr(version_str)})")
                                    print()
                                    version_found = True

                                candidates.append((len(minor), version_str))

                    except UnicodeDecodeError:
                        pass

                    pos += 1

                    if len(candidates) >= 50:
                        break

            except Exception:
                continue

            if len(candidates) >= 50:
                break

        # [STEP 6] Priority Selection
        print(f"[STEP 6] Priority Selection")
        print(f"  Total candidates collected: {len(candidates)}")
        print(f"  candidates (first 5) = {candidates[:5]}")
        print()

        candidates.sort(reverse=True)
        print(f"  After sorting (by minor length, descending):")
        print(f"  candidates (first 5) = {candidates[:5]}")
        print()

        if candidates:
            result = candidates[0][1]
            print(f"  result = candidates[0][1] = {repr(result)}")
            print()
            print("=" * 80)
            print(f"FINAL RESULT: {result}")
            print("=" * 80)
            return result
        else:
            print("  ✗ No candidates found!")
            return None

    finally:
        scanner.close()

if __name__ == "__main__":
    debug_get_version()

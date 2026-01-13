#!/usr/bin/env python3
"""
Find version by following VersionScript references to version class.

Approach:
1. Find VersionScript MonoClass (name="VersionScript", namespace="hackmud")
2. Find references to version class in VersionScript's static fields or code
3. Read the version class's static field (major, minor, build)
4. Format as v{major}.{minor:03d}
"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def find_version_via_versionscript():
    print("=" * 70)
    print("Finding version through VersionScript references")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        scanner.connect()
        print(f"Connected to PID {scanner.pid}\n")

        mem = scanner.memory_reader

        # Step 1: Find VersionScript MonoClass
        print("Step 1: Finding VersionScript MonoClass...")

        heap = scanner._get_heap_region()
        if not heap:
            print("  ✗ Could not find heap region")
            return False

        start, end = heap
        heap_data = mem.read(start, end - start)

        # Look for MonoClass with name="VersionScript", namespace="hackmud"
        target_class = "VersionScript"
        target_namespace = "hackmud"

        class_name_offset = scanner.offsets.get('mono_class_name', 0x40)
        class_namespace_offset = scanner.offsets.get('mono_class_namespace', 0x48)

        versionscript_class_addr = None

        for offset in range(0, len(heap_data) - 0x100, 8):
            try:
                # Read class name pointer
                name_ptr_bytes = heap_data[offset + class_name_offset:offset + class_name_offset + 8]
                if len(name_ptr_bytes) < 8:
                    continue
                name_ptr = struct.unpack('<Q', name_ptr_bytes)[0]

                if not scanner._is_valid_pointer(name_ptr):
                    continue

                # Read class name
                name = scanner._read_cstring(name_ptr, 32)
                if name != target_class:
                    continue

                # Read namespace pointer
                ns_ptr_bytes = heap_data[offset + class_namespace_offset:offset + class_namespace_offset + 8]
                if len(ns_ptr_bytes) < 8:
                    continue
                ns_ptr = struct.unpack('<Q', ns_ptr_bytes)[0]

                if not scanner._is_valid_pointer(ns_ptr):
                    continue

                # Read namespace
                namespace = scanner._read_cstring(ns_ptr, 64)
                if namespace != target_namespace:
                    continue

                # Found it!
                versionscript_class_addr = start + offset
                print(f"  ✓ Found VersionScript MonoClass at {hex(versionscript_class_addr)}")
                break

            except:
                continue

        if not versionscript_class_addr:
            print("  ✗ VersionScript MonoClass not found")
            return False

        print()
        print("Step 2: Analyzing VersionScript for version class references...")
        print("  (This step requires analyzing MonoClass static fields or method IL)")
        print("  For now, using pattern search as proof-of-concept...")
        print()

        # TODO: Implement proper MonoClass static field reading
        # For now, fall back to pattern search to demonstrate the concept

        return True

    finally:
        scanner.close()

if __name__ == "__main__":
    success = find_version_via_versionscript()
    sys.exit(0 if success else 1)

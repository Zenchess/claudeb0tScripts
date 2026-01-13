#!/usr/bin/env python3
"""Test reading version string from VersionScript

Verifies we can find VersionScript instances and read the version from
the Text component at +0x40 → Text.m_Text at +0xd0
"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def read_string(mem, addr):
    """Read a MonoString from memory"""
    if not addr:
        return None

    try:
        # MonoString structure:
        # +0x00: vtable pointer
        # +0x10: length (int32)
        # +0x14: string data (UTF-16)
        length = mem.read_uint32(addr + 0x10)

        if length <= 0 or length > 1000:
            return None

        # Read string data as UTF-16
        data = mem.read(addr + 0x14, length * 2)
        return data.decode('utf-16-le', errors='ignore')
    except:
        return None


def test_version_script():
    """Attempt to find and read version from VersionScript"""

    print("=" * 70)
    print("Testing VersionScript version extraction")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        # Connect to game
        print("[1/4] Connecting to hackmud...")
        scanner.connect()
        print(f"      ✓ Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # Read /proc/PID/maps to find heap regions
        print("[2/4] Scanning memory for version string pattern...")
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

                        # Only scan reasonably-sized regions (< 100MB)
                        if size < 100 * 1024 * 1024:
                            regions.append((start_addr, end_addr))

        print(f"      Found {len(regions)} memory regions to scan")

        # Search for version pattern in memory (both ASCII and UTF-16)
        version_addrs = []
        # Try both ASCII and UTF-16LE encodings
        versions = ['v2.016', 'v2.015', 'v2.014', 'v2.017', 'v2.018']
        patterns = []
        for v in versions:
            patterns.append(v.encode('ascii'))  # ASCII
            patterns.append(v.encode('utf-16-le'))  # UTF-16 (MonoString)

        for start, end in regions:
            try:
                # Read region in chunks
                chunk_size = 1024 * 1024  # 1MB chunks
                for offset in range(0, end - start, chunk_size):
                    addr = start + offset
                    size = min(chunk_size, end - addr)

                    try:
                        data = mem.read(addr, size)

                        for pattern in patterns:
                            pos = 0
                            while True:
                                pos = data.find(pattern, pos)
                                if pos == -1:
                                    break

                                match_addr = addr + pos
                                # Try to decode pattern (might be UTF-16)
                                try:
                                    ver_str = pattern.decode('utf-16-le')
                                except:
                                    ver_str = pattern.decode('ascii')

                                version_addrs.append((match_addr, ver_str))
                                pos += 1
                    except:
                        pass
            except:
                pass

        if not version_addrs:
            print("      ✗ Could not find version string pattern in memory")
            return False

        print(f"      ✓ Found {len(version_addrs)} version string occurrences")
        print()

        # Check each occurrence
        print("[3/4] Analyzing version string occurrences...")

        for i, (ver_addr, ver_str) in enumerate(version_addrs[:10], 1):  # Check first 10
            print(f"      [{i}] Version string '{ver_str}' at {hex(ver_addr)}")

            # Try different MonoString data offsets (+0x14, +0x18)
            found_valid = False
            for data_offset in [0x14, 0x18, 0x1c, 0x20]:
                monostring_addr = ver_addr - data_offset

                # Verify by reading the string
                test_str = read_string(mem, monostring_addr)
                if test_str and ver_str in test_str:
                    print(f"          ✓ Valid MonoString at {hex(monostring_addr)}: '{test_str}' (data offset: +{hex(data_offset)})")
                    found_valid = True
                    break

            if found_valid:
                # Now search backwards in memory for a pointer to this MonoString
                # This would be Text.m_Text field at +0xd0 in Text object

                # Search in nearby memory for pointer to this string
                search_start = max(monostring_addr - 10 * 1024 * 1024, 0x7f0000000000)
                search_size = monostring_addr - search_start

                try:
                    search_data = mem.read(search_start, min(search_size, 5 * 1024 * 1024))
                    ptr_bytes = struct.pack('<Q', monostring_addr)

                    pos = search_data.find(ptr_bytes)
                    if pos != -1:
                        ptr_addr = search_start + pos
                        print(f"          ✓ Found pointer at {hex(ptr_addr)}")

                        # If this is Text.m_Text at +0xd0, Text object is at ptr_addr - 0xd0
                        text_obj_addr = ptr_addr - 0xd0

                        print(f"          → Possible Text object at {hex(text_obj_addr)}")

                        # Now search for pointer to Text object at +0x40 offset
                        # (VersionScript.text_component field)

                        text_ptr_bytes = struct.pack('<Q', text_obj_addr)
                        pos2 = search_data.find(text_ptr_bytes)

                        if pos2 != -1:
                            field_addr = search_start + pos2
                            vs_addr = field_addr - 0x40

                            print(f"          → Possible VersionScript at {hex(vs_addr)}")

                            # Verify the chain
                            try:
                                text_ptr = mem.read_uint64(vs_addr + 0x40)
                                if text_ptr == text_obj_addr:
                                    text_m_text_ptr = mem.read_uint64(text_ptr + 0xd0)
                                    if text_m_text_ptr == monostring_addr:
                                        final_version = read_string(mem, text_m_text_ptr)

                                        print()
                                        print("=" * 70)
                                        print("[4/4] SUCCESS!")
                                        print("=" * 70)
                                        print(f"VersionScript instance: {hex(vs_addr)}")
                                        print(f"  +0x40 → Text object: {hex(text_ptr)}")
                                        print(f"         +0xd0 → MonoString: {hex(text_m_text_ptr)}")
                                        print(f"                Version: '{final_version}'")
                                        print("=" * 70)

                                        return True
                            except:
                                pass

                except:
                    pass

                print()

        print("[4/4] Could not verify complete VersionScript → Text → version chain")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        pass  # Scanner auto-closes


if __name__ == '__main__':
    success = test_version_script()
    print()
    sys.exit(0 if success else 1)

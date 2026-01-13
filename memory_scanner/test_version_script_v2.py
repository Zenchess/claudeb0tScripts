#!/usr/bin/env python3
"""Test reading version string from VersionScript (v2)

Based on Kaj's find_version() example code. Scans for MonoString length fields
to find the version string, then works backwards to find VersionScript.
"""

import sys
import struct
import re
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

# MonoString structure constants
MONO_STRING_LENGTH_OFFSET = 0x10  # Length field is at +0x10 from MonoString start
MONO_STRING_DATA_OFFSET = 0x14    # String data is at +0x14 from MonoString start

def read_mono_string(mem, addr, max_len=100):
    """Read a MonoString from memory"""
    if not addr:
        return None

    try:
        # MonoString structure:
        # +0x00: vtable pointer
        # +0x10: length (int32)
        # +0x14: string data (UTF-16)
        length = mem.read_uint32(addr + MONO_STRING_LENGTH_OFFSET)

        if length <= 0 or length > max_len:
            return None

        # Read string data as UTF-16
        data = mem.read(addr + MONO_STRING_DATA_OFFSET, length * 2)
        return data.decode('utf-16-le', errors='ignore')
    except:
        return None


def find_version(mem, regions):
    """Find game version string by scanning for MonoString with version pattern"""
    # Match exactly: v followed by digits, dot, and more digits (e.g. v2.016)
    version_pattern = re.compile(r'^v\d+\.\d+$')

    candidates = []

    for start, end in regions:
        try:
            data = mem.read(start, end - start)
        except:
            continue

        if not data:
            continue

        # Scan for potential MonoString length fields (small values 5-10)
        for offset in range(0, len(data) - 30, 4):
            length_bytes = data[offset:offset+4]
            if len(length_bytes) < 4:
                continue

            length = struct.unpack('<I', length_bytes)[0]

            if 5 <= length <= 10:  # Version string length e.g. "v2.016" = 6
                # This might be the length field at +0x10 from MonoString start
                # So MonoString is at: (start + offset) - 0x10
                string_addr = (start + offset) - MONO_STRING_LENGTH_OFFSET

                if string_addr > 0:
                    text = read_mono_string(mem, string_addr, 20)
                    if text:
                        text = text.strip()
                        # Only accept clean ASCII version strings
                        if version_pattern.match(text) and all(ord(c) < 128 for c in text):
                            candidates.append((string_addr, text))

    return candidates


def test_version_script_v2():
    """Test finding version using Kaj's method"""

    print("=" * 70)
    print("Testing VersionScript version extraction (v2 - Kaj's method)")
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
        print("[2/3] Scanning memory for version MonoString...")
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

                        # Only scan reasonably-sized regions (< 50MB)
                        if size < 50 * 1024 * 1024:
                            regions.append((start_addr, end_addr))

        print(f"      Scanning {len(regions)} memory regions...")

        # Find version strings
        candidates = find_version(mem, regions)

        if not candidates:
            print("      ✗ Could not find version MonoString")
            return False

        print(f"      ✓ Found {len(candidates)} version string(s)")
        print()

        # Check each candidate
        print("[3/3] Analyzing version string candidates...")

        for i, (string_addr, version) in enumerate(candidates[:10], 1):
            print(f"      [{i}] MonoString at {hex(string_addr)}: '{version}'")

            # Now try to find what points to this MonoString
            # This should be Text.m_Text field at +0xd0 in Text object

            # Search backwards in memory for pointer to this MonoString
            search_start = max(string_addr - 10 * 1024 * 1024, 0x7f0000000000)
            search_size = min(string_addr - search_start, 5 * 1024 * 1024)

            try:
                search_data = mem.read(search_start, search_size)
                ptr_bytes = struct.pack('<Q', string_addr)

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
                                if text_m_text_ptr == string_addr:
                                    final_version = read_mono_string(mem, text_m_text_ptr, 20)

                                    print()
                                    print("=" * 70)
                                    print("SUCCESS!")
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

        print("Could not verify complete VersionScript → Text → MonoString chain")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_version_script_v2()
    print()
    sys.exit(0 if success else 1)

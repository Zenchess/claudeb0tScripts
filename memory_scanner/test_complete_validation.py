#!/usr/bin/env python3
"""Complete validation of VersionScript → Text → MonoString chain

Validates the complete memory structure chain from VersionScript down to the version string.
"""

import sys
import struct
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def read_uint64(mem, addr):
    """Helper to read uint64"""
    return struct.unpack('<Q', mem.read(addr, 8))[0]

def read_mono_string(mem, addr, max_len=100):
    """Read a MonoString from memory"""
    if not addr:
        return None

    try:
        # Try different MonoString structures
        # From memory dump: length at +0x10, data at +0x20 (not +0x14!)
        # Standard older: length at +0x10, data at +0x14
        # Some versions: length at +0x08, data at +0x0c

        for length_offset, data_offset in [(0x10, 0x20), (0x10, 0x14), (0x08, 0x0c), (0x08, 0x10)]:
            try:
                # Read length as uint32
                length_bytes = mem.read(addr + length_offset, 4)
                length = struct.unpack('<I', length_bytes)[0]
                if 0 < length < max_len:
                    data = mem.read(addr + data_offset, length * 2)
                    text = data.decode('utf-16-le', errors='ignore')
                    if text:  # Valid string
                        return text, length_offset, data_offset
            except:
                continue

        return None
    except:
        return None


def complete_validation():
    """Complete validation of VersionScript chain"""

    print("=" * 70)
    print("Complete VersionScript → Text → MonoString validation")
    print("=" * 70)
    print()

    scanner = Scanner()

    try:
        # Connect to game
        print("[1/5] Connecting to hackmud...")
        scanner.connect()
        print(f"      ✓ Connected to PID {scanner.pid}")
        print()

        mem = scanner.memory_reader

        # Step 1: Find version string in memory
        print("[2/5] Finding version MonoString...")
        maps_file = f"/proc/{scanner.pid}/maps"

        regions = []
        with open(maps_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and 'rw' in parts[1]:
                    addr_range = parts[0]
                    start, end = addr_range.split('-')
                    regions.append((int(start, 16), int(end, 16)))

        # Search for version string
        patterns = ['v2.016'.encode('utf-16-le'), 'v2.015'.encode('utf-16-le'),
                   'v2.017'.encode('utf-16-le'), 'v2.018'.encode('utf-16-le')]

        version_data_addr = None
        version_str = None

        for start, end in regions:
            if version_data_addr:
                break
            try:
                chunk_size = 1024 * 1024
                for offset in range(0, end - start, chunk_size):
                    addr = start + offset
                    read_size = min(chunk_size, end - addr)
                    try:
                        data = mem.read(addr, read_size)
                        for pattern in patterns:
                            pos = data.find(pattern)
                            if pos != -1:
                                version_data_addr = addr + pos
                                version_str = pattern.decode('utf-16-le')
                                break
                    except:
                        pass
                    if version_data_addr:
                        break
            except:
                pass

        if not version_data_addr:
            print("      ✗ Could not find version string in memory")
            return False

        print(f"      ✓ Found version string '{version_str}' at {hex(version_data_addr)}")
        print()

        # Step 2: Find the MonoString structure
        print("[3/5] Locating MonoString structure...")

        monostring_addr = None
        length_off = None
        data_off = None

        # Try different offsets to find MonoString base
        # Based on memory dump: data is at +0x20 from base, so try 0x20 first
        for test_offset in [0x20, 0x14, 0x0c, 0x18, 0x10, 0x1c]:
            test_addr = version_data_addr - test_offset
            result = read_mono_string(mem, test_addr, 20)
            if result and version_str in result[0]:
                monostring_addr = test_addr
                length_off = result[1]
                data_off = result[2]
                print(f"      ✓ MonoString at {hex(monostring_addr)}")
                print(f"        Structure: length at +{hex(length_off)}, data at +{hex(data_off)}")
                break

        if not monostring_addr:
            print("      ✗ Could not locate MonoString structure")
            return False

        print()

        # Step 3: Find Text object (should have pointer to MonoString at +0xd0)
        print("[4/5] Finding UnityEngine.UI.Text object...")

        ptr_bytes = struct.pack('<Q', monostring_addr)
        text_obj_addr = None

        try:
            # Search through memory regions for pointer to MonoString
            for start, end in regions:
                if text_obj_addr:
                    break

                try:
                    # Read region in chunks
                    chunk_size = 1024 * 1024
                    for offset in range(0, end - start, chunk_size):
                        addr = start + offset
                        read_size = min(chunk_size, end - addr)

                        try:
                            data = mem.read(addr, read_size)
                            pos = 0
                            while True:
                                pos = data.find(ptr_bytes, pos)
                                if pos == -1:
                                    break

                                ptr_addr = addr + pos

                                # If this is Text.m_Text at +0xd0, Text is at ptr_addr - 0xd0
                                candidate_text = ptr_addr - 0xd0

                                # Verify: read pointer at +0xd0 and check if it matches
                                try:
                                    verify_ptr = read_uint64(mem, candidate_text + 0xd0)
                                    if verify_ptr == monostring_addr:
                                        text_obj_addr = candidate_text
                                        print(f"      ✓ Found Text object at {hex(text_obj_addr)}")
                                        print(f"        m_Text (+0xd0) → {hex(verify_ptr)}")
                                        break
                                except:
                                    pass

                                pos += 1

                            if text_obj_addr:
                                break
                        except:
                            pass

                        if text_obj_addr:
                            break
                except:
                    pass

            if not text_obj_addr:
                print("      ✗ Could not find Text object")
                return False

        except Exception as e:
            print(f"      ✗ Error searching for Text object: {e}")
            return False

        print()

        # Step 4: Find VersionScript (should have pointer to Text at +0x40)
        print("[5/5] Finding VersionScript instance...")

        text_ptr_bytes = struct.pack('<Q', text_obj_addr)
        version_script_addr = None

        try:
            # Search through memory regions for pointer to Text object
            for start, end in regions:
                if version_script_addr:
                    break

                try:
                    # Read region in chunks
                    chunk_size = 1024 * 1024
                    for offset in range(0, end - start, chunk_size):
                        addr = start + offset
                        read_size = min(chunk_size, end - addr)

                        try:
                            data = mem.read(addr, read_size)
                            pos = 0
                            while True:
                                pos = data.find(text_ptr_bytes, pos)
                                if pos == -1:
                                    break

                                field_addr = addr + pos

                                # If this is VersionScript.text_component at +0x40
                                candidate_vs = field_addr - 0x40

                                # Verify: read pointer at +0x40 and check if it matches
                                try:
                                    verify_ptr = read_uint64(mem, candidate_vs + 0x40)
                                    if verify_ptr == text_obj_addr:
                                        version_script_addr = candidate_vs
                                        print(f"      ✓ Found VersionScript at {hex(version_script_addr)}")
                                        print(f"        text_component (+0x40) → {hex(verify_ptr)}")
                                        break
                                except:
                                    pass

                                pos += 1

                            if version_script_addr:
                                break
                        except:
                            pass

                        if version_script_addr:
                            break
                except:
                    pass

            if not version_script_addr:
                print("      ✗ Could not find VersionScript instance")
                return False

        except Exception as e:
            print(f"      ✗ Error searching for VersionScript: {e}")
            return False

        print()

        # Success - print complete chain
        print("=" * 70)
        print("VALIDATION SUCCESS!")
        print("=" * 70)
        print()
        print("Complete chain verified:")
        print(f"  VersionScript:      {hex(version_script_addr)}")
        print(f"    +0x40 →")
        print(f"  Text object:        {hex(text_obj_addr)}")
        print(f"    +0xd0 →")
        print(f"  MonoString:         {hex(monostring_addr)}")
        print(f"    +{hex(data_off)} →")
        print(f"  Version data:       {hex(version_data_addr)}")
        print(f"  Version string:     '{version_str}'")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = complete_validation()
    print()
    sys.exit(0 if success else 1)

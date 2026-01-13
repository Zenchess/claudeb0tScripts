#!/usr/bin/env python3
"""Find version by locating VersionScript MonoBehaviour and following references

This approach:
1. Finds VersionScript MonoBehaviour class
2. Scans for VersionScript instances (by vtable)
3. From VersionScript, follows references to Text component
4. From Text, reads m_Text field to get version MonoString
"""

import sys
import struct
import re
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python_lib"))

from hackmud.memory import Scanner

def read_uint64(mem, addr):
    """Helper to read uint64"""
    try:
        return struct.unpack('<Q', mem.read(addr, 8))[0]
    except:
        return None

def read_uint32(mem, addr):
    """Helper to read uint32"""
    try:
        return struct.unpack('<I', mem.read(addr, 4))[0]
    except:
        return None

def read_mono_string(mem, addr, max_len=100):
    """Read a MonoString from memory"""
    if not addr:
        return None

    try:
        # Try different MonoString structures
        for length_offset, data_offset in [(0x10, 0x20), (0x10, 0x14), (0x08, 0x0c)]:
            try:
                length = read_uint32(mem, addr + length_offset)
                if length and 0 < length < max_len:
                    data = mem.read(addr + data_offset, length * 2)
                    text = data.decode('utf-16-le', errors='ignore')
                    if text:
                        return text.strip()
            except:
                continue
        return None
    except:
        return None

def find_version_via_script():
    """Find version by locating VersionScript first"""

    print("=" * 70)
    print("Finding version via VersionScript → Text → MonoString")
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

        # Step 1: Find VersionScript class name
        print("[2/4] Searching for VersionScript...")
        print("      Looking for 'VersionScript' string in memory...")

        maps_file = f"/proc/{scanner.pid}/maps"
        regions = []
        with open(maps_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and 'rw' in parts[1]:
                    addr_range = parts[0]
                    start, end = addr_range.split('-')
                    regions.append((int(start, 16), int(end, 16)))

        # Search for "VersionScript" as ASCII string
        search_bytes = b'VersionScript\x00'
        version_script_name_addr = None

        for start, end in regions:
            if version_script_name_addr:
                break
            if end - start > 100 * 1024 * 1024:  # Skip huge regions
                continue
            try:
                data = mem.read(start, end - start)
                pos = data.find(search_bytes)
                if pos != -1:
                    version_script_name_addr = start + pos
                    print(f"      ✓ Found 'VersionScript' string at {hex(version_script_name_addr)}")
                    break
            except:
                pass

        if not version_script_name_addr:
            print("      ✗ Could not find 'VersionScript' string")
            return False

        print()

        # Step 2: Find VersionScript instances
        print("[3/4] Searching for VersionScript instances...")
        print("      (Scanning memory for MonoBehaviour objects...)")

        # MonoBehaviour objects have:
        # - vtable pointer at +0x0
        # - MonoClass pointer nearby
        # We'll scan for objects and check if they reference our VersionScript class

        # Actually, let's try a different approach:
        # Search for pointers TO the VersionScript name string
        # These pointers would be in MonoClass structures (name field)

        name_ptr_bytes = struct.pack('<Q', version_script_name_addr)
        monoclass_candidates = []

        for start, end in regions:
            if end - start > 100 * 1024 * 1024:
                continue
            try:
                data = mem.read(start, end - start)
                pos = 0
                while True:
                    pos = data.find(name_ptr_bytes, pos)
                    if pos == -1:
                        break
                    ptr_addr = start + pos
                    # This could be the 'name' field in MonoClass
                    # MonoClass has name at +0x30 in some versions
                    # So MonoClass would be at ptr_addr - 0x30
                    monoclass_candidates.append(ptr_addr)
                    pos += 1
            except:
                pass

        print(f"      Found {len(monoclass_candidates)} potential MonoClass pointers")

        # For each candidate, try to find vtable and then instances
        version_script_addr = None
        text_component_addr = None

        for candidate_name_ptr in monoclass_candidates[:10]:  # Try first 10
            # Assume name is at +0x30 from MonoClass base
            for name_offset in [0x30, 0x48, 0x50]:
                monoclass_addr = candidate_name_ptr - name_offset

                # Read runtime_info pointer (+0xC8 from MonoClass)
                runtime_info = read_uint64(mem, monoclass_addr + 0xC8)
                if not runtime_info:
                    continue

                # Read vtable from runtime_info (+0x8)
                vtable = read_uint64(mem, runtime_info + 0x8)
                if not vtable or vtable < 0x1000:
                    continue

                print(f"      Checking MonoClass at {hex(monoclass_addr)}, vtable {hex(vtable)}")

                # Now scan for instances with this vtable
                vtable_bytes = struct.pack('<Q', vtable)

                for start, end in regions[:50]:  # Check first 50 regions
                    if version_script_addr:
                        break
                    if end - start > 50 * 1024 * 1024:
                        continue

                    try:
                        chunk_size = 1024 * 1024
                        for offset in range(0, end - start, chunk_size):
                            addr = start + offset
                            read_size = min(chunk_size, end - addr)
                            data = mem.read(addr, read_size)

                            pos = data.find(vtable_bytes)
                            if pos != -1:
                                instance_addr = addr + pos
                                print(f"      ✓ Found VersionScript instance at {hex(instance_addr)}")
                                version_script_addr = instance_addr
                                break
                    except:
                        pass

                if version_script_addr:
                    break

            if version_script_addr:
                break

        if not version_script_addr:
            print("      ✗ Could not find VersionScript instance")
            return False

        print()

        # Step 3: Follow references from VersionScript to Text to MonoString
        print("[4/4] Following references to find version string...")

        # VersionScript is a MonoBehaviour, which has GameObject reference
        # The GameObject has components, including the Text component
        # This is complex, so let's try a simpler approach:

        # Search for version string near the VersionScript instance
        # Or search in nearby memory for Text object

        print("      Searching for Text component references...")

        # Read memory around VersionScript instance
        try:
            nearby_data = mem.read(version_script_addr, 1024)

            # Look for pointers in this data
            for i in range(0, len(nearby_data) - 8, 8):
                ptr = struct.unpack('<Q', nearby_data[i:i+8])[0]
                if ptr > 0x1000:  # Valid pointer
                    # Try to read this as Text object with m_Text field
                    for text_offset in [0xd0, 0xc8, 0xd8, 0xe0]:
                        monostring_ptr = read_uint64(mem, ptr + text_offset)
                        if monostring_ptr and monostring_ptr > 0x1000:
                            version_text = read_mono_string(mem, monostring_ptr, 20)
                            if version_text and re.match(r'^v\d+\.\d+', version_text):
                                print(f"      ✓ Found version via Text at {hex(ptr)}")
                                print(f"        m_Text (+{hex(text_offset)}) → {hex(monostring_ptr)}")
                                print(f"        Version: {version_text}")
                                return True

        except Exception as e:
            print(f"      ✗ Error following references: {e}")

        print("      ✗ Could not find Text component with version string")
        return False

    finally:
        scanner.close()

if __name__ == "__main__":
    success = find_version_via_script()
    sys.exit(0 if success else 1)

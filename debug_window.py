#!/usr/bin/env python3
"""Debug Window instances - dump raw memory"""

import struct
import os
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class MemoryRegion:
    start: int
    end: int
    perms: str
    path: str

def get_hackmud_pid() -> Optional[int]:
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    if 'hackmud' in f.read():
                        return int(pid)
            except:
                pass
    return None

def get_regions(pid: int) -> List[MemoryRegion]:
    regions = []
    with open(f'/proc/{pid}/maps', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 5:
                continue
            addr_range = parts[0].split('-')
            start = int(addr_range[0], 16)
            end = int(addr_range[1], 16)
            perms = parts[1]
            path = parts[-1] if len(parts) > 5 else ''
            regions.append(MemoryRegion(start, end, perms, path))
    return regions

def is_valid_ptr(ptr: int, regions: List[MemoryRegion]) -> bool:
    if ptr < 0x1000 or ptr > 0x7FFFFFFFFFFF:
        return False
    for region in regions:
        if region.start <= ptr < region.end and 'r' in region.perms:
            return True
    return False

def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"PID: {pid}")
    regions = get_regions(pid)
    mem = open(f'/proc/{pid}/mem', 'rb')

    def read_ptr(addr):
        try:
            mem.seek(addr)
            data = mem.read(8)
            if len(data) == 8:
                return struct.unpack('<Q', data)[0]
        except:
            pass
        return None

    def read_bytes(addr, size):
        try:
            mem.seek(addr)
            return mem.read(size)
        except:
            return None

    def read_cstring(addr, max_len=256):
        data = read_bytes(addr, max_len)
        if not data:
            return None
        try:
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8', errors='replace')
        except:
            return None

    def read_mono_string(addr):
        """Read MonoString (UTF-16)"""
        if not addr or addr < 0x1000:
            return None
        # MonoString layout: vtable(8), sync_block(8), length(4), padding(0), data...
        # Actually MonoString: vtable(8), length at +0x10, data at +0x14
        length_data = read_bytes(addr + 0x10, 4)
        if not length_data or len(length_data) != 4:
            return None
        length = struct.unpack('<I', length_data)[0]
        if length < 0 or length > 10000:
            return None
        if length == 0:
            return ""
        data = read_bytes(addr + 0x14, length * 2)
        if not data:
            return None
        try:
            return data.decode('utf-16-le', errors='replace')
        except:
            return None

    # Get Window instances
    from mono_reader_v2 import MonoReaderV2
    with MonoReaderV2(pid) as mono:
        result = mono.find_window_class()
        if not result:
            print("Window class not found")
            mem.close()
            return

        class_addr, vtable = result
        print(f"Window class: 0x{class_addr:x}, vtable: 0x{vtable:x}")
        window_instances = mono.find_window_instances(vtable)
        print(f"Found {len(window_instances)} instances\n")

    # Analyze each instance
    for i, win_addr in enumerate(window_instances):
        print(f"\n=== Window instance {i} at 0x{win_addr:x} ===")

        # Verify vtable
        vt = read_ptr(win_addr)
        print(f"vtable: 0x{vt:x} (expected: 0x{vtable:x}) {'OK' if vt == vtable else 'MISMATCH'}")

        # Dump first 512 bytes as pointers
        print("\nPointer fields (checking for valid ptrs and strings):")
        for off in range(0x8, 0x200, 8):
            ptr = read_ptr(win_addr + off)
            if ptr and is_valid_ptr(ptr, regions):
                # Try as C string
                cstr = read_cstring(ptr, 32)
                # Try as MonoString
                mstr = read_mono_string(ptr)

                extra = ""
                if cstr and len(cstr) > 2 and cstr.isprintable():
                    extra += f' cstr="{cstr[:30]}"'
                if mstr and len(mstr) > 0:
                    extra += f' mstr="{mstr[:30]}"'

                # Follow one level - check if it's another object with strings
                ptr2 = read_ptr(ptr + 0x10)
                if ptr2 and is_valid_ptr(ptr2, regions):
                    mstr2 = read_mono_string(ptr2)
                    if mstr2 and len(mstr2) > 0:
                        extra += f' ->mstr="{mstr2[:30]}"'

                if extra or off < 0x80:
                    print(f"  +0x{off:02x}: 0x{ptr:016x}{extra}")

        # Only show first 3 instances in detail
        if i >= 2:
            print("  (truncating output...)")
            break

    mem.close()

if __name__ == '__main__':
    main()

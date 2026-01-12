#!/usr/bin/env python3
"""Find 'scratch' string to identify labelName offset"""

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

def is_valid_ptr(ptr, regions):
    if ptr < 0x1000 or ptr > 0x7FFFFFFFFFFF:
        return False
    for r in regions:
        if r.start <= ptr < r.end and 'r' in r.perms:
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

    def read_bytes(addr, size):
        try:
            mem.seek(addr)
            return mem.read(size)
        except:
            return None

    def read_ptr(addr):
        data = read_bytes(addr, 8)
        if data and len(data) == 8:
            return struct.unpack('<Q', data)[0]
        return None

    # Get heap region
    heap = None
    for r in regions:
        if '[heap]' in r.path:
            heap = r
            break

    if not heap:
        print("No heap found")
        mem.close()
        return

    print(f"Heap: 0x{heap.start:x} - 0x{heap.end:x} ({(heap.end-heap.start)//1024}KB)")

    # Search for "scratch" as UTF-16
    search_patterns = [
        b's\x00c\x00r\x00a\x00t\x00c\x00h\x00',  # UTF-16LE "scratch"
        b'scratch',  # ASCII
        b'shell',    # another window type
        b's\x00h\x00e\x00l\x00l\x00',  # UTF-16LE "shell"
        b'chat',     # chat window
        b'c\x00h\x00a\x00t\x00',  # UTF-16LE "chat"
    ]

    data = read_bytes(heap.start, heap.end - heap.start)
    if not data:
        print("Could not read heap")
        mem.close()
        return

    print("\nSearching for window label strings...")
    for pattern in search_patterns:
        pos = 0
        count = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            addr = heap.start + pos
            # Check surrounding data
            context = data[max(0,pos-16):pos+len(pattern)+16]

            # Check if this looks like a MonoString (preceded by length)
            if pos >= 4:
                pre_data = data[pos-4:pos]
                length = struct.unpack('<I', pre_data)[0]
                if length == len(pattern)//2:  # UTF-16 length
                    print(f"  {pattern[:20]!r} at 0x{addr:x} (looks like MonoString, len={length})")
                    # Find what points to this string
                    string_obj_addr = addr - 0x14  # String object start
                    print(f"    String object at 0x{string_obj_addr:x}")

                    # Search heap for pointers to this string object
                    ptr_bytes = struct.pack('<Q', string_obj_addr)
                    ptr_pos = 0
                    refs_found = 0
                    while refs_found < 5:
                        ptr_pos = data.find(ptr_bytes, ptr_pos)
                        if ptr_pos == -1:
                            break
                        ref_addr = heap.start + ptr_pos
                        print(f"    Referenced from: 0x{ref_addr:x}")
                        refs_found += 1
                        ptr_pos += 8

            count += 1
            pos += 1
            if count > 5:
                print(f"  ... ({count}+ more)")
                break

    # Also look for Window instances directly
    print("\n--- Window instances and their fields ---")
    from mono_reader_v2 import MonoReaderV2
    with MonoReaderV2(pid) as mono:
        result = mono.find_window_class()
        if result:
            class_addr, vtable = result
            windows = mono.find_window_instances(vtable)
            print(f"Found {len(windows)} Window instances")

            # For each window, search nearby memory for string patterns
            for i, win in enumerate(windows):
                win_data = read_bytes(win, 0x300)
                if not win_data:
                    continue

                print(f"\nWindow {i} at 0x{win:x}:")

                # Look for "scratch" or similar in the instance data
                for j in range(0, len(win_data)-8, 8):
                    ptr = struct.unpack('<Q', win_data[j:j+8])[0]
                    if is_valid_ptr(ptr, regions):
                        # Try to read string at various offsets
                        for str_offset in [0, 0xC, 0x10, 0x14]:
                            str_data = read_bytes(ptr + str_offset, 50)
                            if str_data:
                                # Check for ASCII printable
                                if all(32 <= b < 127 or b == 0 for b in str_data[:20]):
                                    try:
                                        text = str_data.split(b'\x00')[0].decode('ascii')
                                        if len(text) > 2 and text.isprintable():
                                            print(f"  +0x{j:x} -> +0x{str_offset:x}: \"{text[:30]}\"")
                                    except:
                                        pass
                                # Check for UTF-16
                                if len(str_data) >= 4:
                                    try:
                                        text = str_data[:40].decode('utf-16-le', errors='ignore').split('\x00')[0]
                                        if len(text) > 2 and text.isprintable():
                                            print(f"  +0x{j:x} -> +0x{str_offset:x} (u16): \"{text[:30]}\"")
                                    except:
                                        pass

                if i >= 2:
                    print("(truncating...)")
                    break

    mem.close()

if __name__ == '__main__':
    main()

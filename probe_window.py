#!/usr/bin/env python3
"""Probe Window instances to find field offsets"""

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

class MemReader:
    def __init__(self, pid: int):
        self.mem = open(f'/proc/{pid}/mem', 'rb')
        self.regions = get_regions(pid)

    def close(self):
        self.mem.close()

    def read_bytes(self, addr: int, size: int) -> Optional[bytes]:
        try:
            self.mem.seek(addr)
            return self.mem.read(size)
        except:
            return None

    def read_ptr(self, addr: int) -> Optional[int]:
        data = self.read_bytes(addr, 8)
        if data and len(data) == 8:
            return struct.unpack('<Q', data)[0]
        return None

    def read_int32(self, addr: int) -> Optional[int]:
        data = self.read_bytes(addr, 4)
        if data and len(data) == 4:
            return struct.unpack('<I', data)[0]
        return None

    def read_cstring(self, addr: int, max_len: int = 256) -> Optional[str]:
        data = self.read_bytes(addr, max_len)
        if not data:
            return None
        try:
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8')
        except:
            return None

    def read_mono_string(self, addr: int) -> Optional[str]:
        """Read MonoString (UTF-16 encoded)"""
        if not addr or addr < 0x1000:
            return None
        # MonoString: vtable at 0x0, length at 0x10, data at 0x14
        length = self.read_int32(addr + 0x10)
        if length is None or length < 0 or length > 10000:
            return None
        if length == 0:
            return ""
        data = self.read_bytes(addr + 0x14, length * 2)
        if data is None:
            return None
        try:
            return data.decode('utf-16-le')
        except:
            return None

    def is_valid(self, ptr: int) -> bool:
        return is_valid_ptr(ptr, self.regions)


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"PID: {pid}")
    reader = MemReader(pid)

    # Window instances from mono_reader_v2.py (need to run it first to get these)
    # Using the vtable-based approach
    import subprocess
    result = subprocess.run(['python3', 'mono_reader_v2.py'], capture_output=True, text=True, cwd='/home/jacob/hackmud')

    # Parse Window instances from output
    window_instances = []
    for line in result.stdout.split('\n'):
        if 'Window instances' in line:
            # Extract instance addresses from the next lines
            continue
        if line.strip().startswith('0x') and len(line.strip()) < 20:
            try:
                addr = int(line.strip(), 16)
                window_instances.append(addr)
            except:
                pass

    if not window_instances:
        print("No Window instances found. Running inline search...")
        # Inline search for Window vtable
        from mono_reader_v2 import MonoReaderV2
        with MonoReaderV2(pid) as mono:
            result = mono.find_window_class()
            if result:
                class_addr, vtable = result
                print(f"Window class: 0x{class_addr:x}, vtable: 0x{vtable:x}")
                window_instances = mono.find_window_instances(vtable)
                print(f"Found {len(window_instances)} instances")

    if not window_instances:
        print("Still no Window instances")
        reader.close()
        return

    print(f"\nProbing {len(window_instances)} Window instances...")
    print("Looking for labelName (string) and output (NMOPNOICKDJ) fields\n")

    # Window fields from decompiled code (approximate offsets):
    # MonoBehaviour base ~0x18-0x20
    # Fields start around offset 0x18 or so
    # Each reference field is 8 bytes on x64

    for i, win_addr in enumerate(window_instances):
        print(f"\n=== Window instance {i} at 0x{win_addr:x} ===")

        # Search for string fields (labelName)
        print("String fields found:")
        for off in range(0x18, 0x200, 8):
            ptr = reader.read_ptr(win_addr + off)
            if ptr and reader.is_valid(ptr):
                s = reader.read_mono_string(ptr)
                if s is not None and len(s) > 0 and len(s) < 100:
                    # Filter likely strings
                    if s.isprintable() and not s.startswith('\x00'):
                        print(f"  +0x{off:x}: \"{s}\"")

        # Search for potential NMOPNOICKDJ objects (look for objects with Queue<string>)
        print("\nPotential output objects (with Queue-like structure):")
        for off in range(0x18, 0x200, 8):
            ptr = reader.read_ptr(win_addr + off)
            if ptr and reader.is_valid(ptr):
                # NMOPNOICKDJ first field after vtable should be Queue<string>
                # Queue has: _array, _head, _tail, _size fields
                queue_ptr = reader.read_ptr(ptr + 0x10)  # First field after vtable
                if queue_ptr and reader.is_valid(queue_ptr):
                    # Check if it looks like a Queue (has array at +0x10)
                    array_ptr = reader.read_ptr(queue_ptr)
                    if array_ptr and reader.is_valid(array_ptr):
                        # Try to read first element
                        elem_ptr = reader.read_ptr(array_ptr + 0x20)  # Array data starts at +0x20
                        if elem_ptr and reader.is_valid(elem_ptr):
                            s = reader.read_mono_string(elem_ptr)
                            if s and ('>>>' in s or '<color' in s or len(s) > 20):
                                print(f"  +0x{off:x}: potential output! First elem: \"{s[:50]}...\"")

    reader.close()

if __name__ == '__main__':
    main()

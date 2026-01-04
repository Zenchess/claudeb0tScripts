#!/usr/bin/env python3
"""Check domain_assemblies GSList"""

import struct
import os
import subprocess
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

    def __del__(self):
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

    def read_cstring(self, addr: int, max_len: int = 256) -> Optional[str]:
        data = self.read_bytes(addr, max_len)
        if not data:
            return None
        try:
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8')
        except:
            return None


def find_root_domain(reader: MemReader, pid: int) -> Optional[int]:
    regions = get_regions(pid)
    for region in regions:
        if 'libmonobdwgc-2.0.so' in region.path and region.perms.startswith('r-x'):
            mono_base = region.start
            mono_path = region.path
            result = subprocess.run(['readelf', '-s', mono_path], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'mono_get_root_domain' in line and 'FUNC' in line:
                    parts = line.split()
                    sym_value = int(parts[1], 16)
                    func_addr = mono_base + sym_value
                    offset_data = reader.read_bytes(func_addr + 3, 4)
                    if offset_data:
                        rel_offset = struct.unpack('<i', offset_data)[0]
                        root_domain_ptr = func_addr + 7 + rel_offset
                        return reader.read_ptr(root_domain_ptr)
    return None


def walk_gslist(reader: MemReader, head: int, regions: List[MemoryRegion]):
    """Walk a GSList and return all data pointers"""
    items = []
    current = head
    seen = set()
    while current and current not in seen and is_valid_ptr(current, regions):
        seen.add(current)
        # GSList: { gpointer data; GSList *next; }
        data = reader.read_ptr(current)
        next_ptr = reader.read_ptr(current + 8)
        if data:
            items.append(data)
        current = next_ptr
        if len(items) > 100:  # Safety limit
            break
    return items


def get_assembly_info(reader: MemReader, assembly: int, regions: List[MemoryRegion]) -> Optional[dict]:
    """Extract assembly name from MonoAssembly"""
    # MonoAssembly offsets (try various common ones)
    for image_offset in [0x60, 0x58, 0x50, 0x48, 0x40, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38, 0x68, 0x70]:
        image = reader.read_ptr(assembly + image_offset)
        if image and is_valid_ptr(image, regions):
            # MonoImage.name is at various offsets
            for name_offset in [0x18, 0x10, 0x20, 0x28, 0x08]:
                name_ptr = reader.read_ptr(image + name_offset)
                if name_ptr and is_valid_ptr(name_ptr, regions):
                    name = reader.read_cstring(name_ptr, 64)
                    if name and '.dll' in name.lower():
                        return {"image_offset": image_offset, "name_offset": name_offset, "name": name}
    return None


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"Found hackmud PID: {pid}")
    regions = get_regions(pid)
    reader = MemReader(pid)

    root_domain = find_root_domain(reader, pid)
    if not root_domain:
        print("Could not find root domain")
        return

    print(f"Root domain: 0x{root_domain:x}")

    # Try various offsets for domain_assemblies
    print("\nSearching for domain_assemblies GSList...")

    for offset in [0x98, 0x90, 0x88, 0x80, 0xa0, 0xb0, 0xc0]:
        ptr = reader.read_ptr(root_domain + offset)
        if not ptr or not is_valid_ptr(ptr, regions):
            continue

        print(f"\n--- Checking offset 0x{offset:x} = 0x{ptr:x} ---")

        # Walk as GSList
        items = walk_gslist(reader, ptr, regions)
        if items:
            print(f"  Found {len(items)} GSList items")
            for i, item in enumerate(items[:10]):  # Show first 10
                info = get_assembly_info(reader, item, regions)
                if info:
                    print(f"    [{i}] 0x{item:x} -> {info['name']} (image@+0x{info['image_offset']:x}, name@+0x{info['name_offset']:x})")
                else:
                    print(f"    [{i}] 0x{item:x} (could not parse as assembly)")


if __name__ == '__main__':
    main()

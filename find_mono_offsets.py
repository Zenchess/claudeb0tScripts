#!/usr/bin/env python3
"""Find MonoDomain struct offsets by scanning memory around root domain"""

import struct
import os
import subprocess
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class MemoryRegion:
    start: int
    end: int
    perms: str
    path: str

    @property
    def size(self) -> int:
        return self.end - self.start


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


def is_valid_heap_ptr(ptr: int, regions: List[MemoryRegion]) -> bool:
    """Check if pointer points to readable memory"""
    if ptr < 0x1000 or ptr > 0x7FFFFFFFFFFF:
        return False
    for region in regions:
        if region.start <= ptr < region.end and 'r' in region.perms:
            return True
    return False


def read_bytes(mem_file, address: int, size: int) -> Optional[bytes]:
    try:
        mem_file.seek(address)
        return mem_file.read(size)
    except:
        return None


def read_ptr(mem_file, address: int) -> Optional[int]:
    data = read_bytes(mem_file, address, 8)
    if data and len(data) == 8:
        return struct.unpack('<Q', data)[0]
    return None


def read_int32(mem_file, address: int) -> Optional[int]:
    data = read_bytes(mem_file, address, 4)
    if data and len(data) == 4:
        return struct.unpack('<I', data)[0]
    return None


def read_cstring(mem_file, address: int, max_len: int = 256) -> Optional[str]:
    data = read_bytes(mem_file, address, max_len)
    if not data:
        return None
    try:
        null_idx = data.index(b'\x00')
        return data[:null_idx].decode('utf-8')
    except:
        return None


def find_root_domain(pid: int, mem_file) -> Optional[int]:
    """Find mono root domain"""
    regions = get_regions(pid)

    # Find libmonobdwgc-2.0.so
    mono_base = None
    mono_path = None
    for region in regions:
        if 'libmonobdwgc-2.0.so' in region.path and region.perms.startswith('r-x'):
            mono_base = region.start
            mono_path = region.path
            break

    if not mono_base:
        print("Could not find libmonobdwgc-2.0.so")
        return None

    print(f"Found mono at 0x{mono_base:x}: {mono_path}")

    # Find mono_get_root_domain symbol
    result = subprocess.run(['readelf', '-s', mono_path], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'mono_get_root_domain' in line and 'FUNC' in line:
            parts = line.split()
            sym_value = int(parts[1], 16)
            func_addr = mono_base + sym_value
            print(f"mono_get_root_domain at 0x{func_addr:x}")

            # Read RIP-relative offset
            offset_data = read_bytes(mem_file, func_addr + 3, 4)
            if offset_data:
                rel_offset = struct.unpack('<i', offset_data)[0]
                root_domain_ptr = func_addr + 7 + rel_offset
                root_domain = read_ptr(mem_file, root_domain_ptr)
                return root_domain
    return None


def scan_domain_struct(pid: int, mem_file, root_domain: int, regions: List[MemoryRegion]):
    """Scan MonoDomain struct to find field offsets"""
    print(f"\nScanning MonoDomain at 0x{root_domain:x}")
    print("=" * 70)

    # Scan the first 512 bytes of the domain struct
    for offset in range(0, 512, 8):
        ptr = read_ptr(mem_file, root_domain + offset)
        if ptr is None:
            continue

        # Check if it's a valid pointer
        valid = is_valid_heap_ptr(ptr, regions)

        # Try to identify what this might be
        info = ""
        if valid:
            # Check if it points to a string (could be friendly_name)
            maybe_str = read_cstring(mem_file, ptr, 64)
            if maybe_str and len(maybe_str) > 2 and maybe_str.isprintable():
                info = f"STRING: \"{maybe_str}\""
            else:
                # Check if it's a GSList (domain_assemblies)
                # GSList: { data (ptr), next (ptr) }
                gslist_data = read_ptr(mem_file, ptr)
                gslist_next = read_ptr(mem_file, ptr + 8)
                if gslist_data and is_valid_heap_ptr(gslist_data, regions):
                    # Could be a GSList, check if data points to MonoAssembly
                    # MonoAssembly has image at offset 0x60
                    image = read_ptr(mem_file, gslist_data + 0x60)
                    if image and is_valid_heap_ptr(image, regions):
                        # MonoImage has name at offset 0x18
                        name_ptr = read_ptr(mem_file, image + 0x18)
                        if name_ptr:
                            name = read_cstring(mem_file, name_ptr, 64)
                            if name:
                                info = f"GSLIST -> Assembly -> Image: \"{name}\""

        # Also try reading as int32 pair
        int_val = read_int32(mem_file, root_domain + offset)
        int_val2 = read_int32(mem_file, root_domain + offset + 4)

        if ptr == 0:
            print(f"  +0x{offset:03x}: NULL")
        elif valid:
            if info:
                print(f"  +0x{offset:03x}: 0x{ptr:016x} (valid ptr) {info}")
            else:
                print(f"  +0x{offset:03x}: 0x{ptr:016x} (valid ptr)")
        elif int_val is not None and int_val < 1000 and int_val2 is not None and int_val2 < 1000:
            # Likely small integers (domain_id, shadow_serial, etc.)
            print(f"  +0x{offset:03x}: int32s: {int_val}, {int_val2}")
        else:
            # Show as hex anyway for reference
            if ptr != 0:
                print(f"  +0x{offset:03x}: 0x{ptr:016x}")


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"Found hackmud PID: {pid}")

    with open(f'/proc/{pid}/mem', 'rb') as mem_file:
        regions = get_regions(pid)
        root_domain = find_root_domain(pid, mem_file)
        if root_domain:
            print(f"Root domain: 0x{root_domain:x}")
            scan_domain_struct(pid, mem_file, root_domain, regions)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Mono memory reader v2 - proper vtable-based approach

Based on:
- https://github.com/wetware-enterprises/scribe/
- https://github.com/AkiraYasha/loki/

This finds hackmud's terminal output by:
1. Finding libmonobdwgc-2.0.so and mono_get_root_domain symbol
2. Walking Mono runtime structures to find Window class
3. Getting vtable address from class
4. Scanning heap for Window instances
5. Following fixed offsets to Queue<string>
"""

import struct
import os
import re
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


class MonoReaderV2:
    # Linux-specific offsets (from scribe/loki)
    MONO_DOMAIN_ASSEMBLIES = 0x98
    MONO_ASSEMBLY_IMAGE = 0x60
    MONO_IMAGE_NAME = 0x18
    MONO_IMAGE_CLASSES = 0x4D0
    MONO_CLASS_NAME = 0x40
    MONO_CLASS_NAMESPACE = 0x48
    MONO_CLASS_RUNTIME_INFO = 0xC8
    MONO_RUNTIME_INFO_VTABLE = 0x8

    # MonoString offsets
    MONO_STRING_LENGTH = 0x10
    MONO_STRING_DATA = 0x14

    # Queue<T> offsets (System.Collections.Generic)
    QUEUE_ITEMS = 0x10  # T[] _array
    QUEUE_HEAD = 0x18   # int _head
    QUEUE_TAIL = 0x1C   # int _tail
    QUEUE_SIZE = 0x20   # int _size

    def __init__(self, pid: int):
        self.pid = pid
        self.mem_file = None
        self.mono_base = None
        self.root_domain = None

    def __enter__(self):
        self.mem_file = open(f'/proc/{self.pid}/mem', 'rb')
        return self

    def __exit__(self, *args):
        if self.mem_file:
            self.mem_file.close()

    def get_regions(self) -> List[MemoryRegion]:
        """Get memory regions from /proc/[pid]/maps"""
        regions = []
        with open(f'/proc/{self.pid}/maps', 'r') as f:
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

    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """Read bytes from memory"""
        if address < 0 or address > 0x7FFFFFFFFFFF or size < 0:
            return None
        try:
            self.mem_file.seek(address)
            return self.mem_file.read(size)
        except (OSError, IOError, ValueError):
            return None

    def read_ptr(self, address: int) -> Optional[int]:
        """Read 64-bit pointer"""
        data = self.read_bytes(address, 8)
        if data and len(data) == 8:
            return struct.unpack('<Q', data)[0]
        return None

    def read_int32(self, address: int) -> Optional[int]:
        """Read 32-bit integer"""
        data = self.read_bytes(address, 4)
        if data and len(data) == 4:
            return struct.unpack('<I', data)[0]
        return None

    def read_cstring(self, address: int, max_len: int = 256) -> Optional[str]:
        """Read null-terminated C string"""
        data = self.read_bytes(address, max_len)
        if not data:
            return None
        try:
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return None

    def read_mono_string(self, address: int) -> Optional[str]:
        """Read MonoString (UTF-16)"""
        if not address or address < 0x1000:
            return None
        length = self.read_int32(address + self.MONO_STRING_LENGTH)
        if length is None or length < 0 or length > 100000:
            return None
        if length == 0:
            return ""
        data = self.read_bytes(address + self.MONO_STRING_DATA, length * 2)
        if data is None:
            return None
        try:
            return data.decode('utf-16-le')
        except:
            return None

    def find_mono_library(self) -> Optional[Tuple[int, str]]:
        """Find libmonobdwgc-2.0.so in process maps"""
        for region in self.get_regions():
            if 'libmonobdwgc-2.0.so' in region.path and region.perms.startswith('r-x'):
                return (region.start, region.path)
        return None

    def find_root_domain(self) -> Optional[int]:
        """Find mono root domain via mono_get_root_domain symbol"""
        mono_info = self.find_mono_library()
        if not mono_info:
            print("Could not find libmonobdwgc-2.0.so")
            return None

        base_addr, path = mono_info
        print(f"Found mono at 0x{base_addr:x}: {path}")

        # Use readelf to find mono_get_root_domain symbol
        try:
            result = subprocess.run(
                ['readelf', '-s', path],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'mono_get_root_domain' in line:
                    parts = line.split()
                    # Format: num: value size type bind vis ndx name
                    sym_value = int(parts[1].rstrip(':'), 16)
                    func_addr = base_addr + sym_value
                    print(f"Found mono_get_root_domain at 0x{func_addr:x}")

                    # Read relative offset from function (RIP-relative addressing)
                    # Pattern: mov rax, [rip+offset] at +3, offset is 4 bytes
                    offset_data = self.read_bytes(func_addr + 3, 4)
                    if offset_data:
                        rel_offset = struct.unpack('<i', offset_data)[0]
                        root_domain_ptr = func_addr + 7 + rel_offset
                        root_domain = self.read_ptr(root_domain_ptr)
                        if root_domain:
                            print(f"Root domain at 0x{root_domain:x}")
                            return root_domain
                    break
        except Exception as e:
            print(f"Error finding symbol: {e}")
            return None

        return None

    def find_window_vtable(self) -> Optional[int]:
        """Find Window class vtable by walking Mono structures"""
        if not self.root_domain:
            self.root_domain = self.find_root_domain()
        if not self.root_domain:
            return None

        # Read assemblies linked list head
        assemblies_ptr = self.read_ptr(self.root_domain + self.MONO_DOMAIN_ASSEMBLIES)
        print(f"Assemblies at 0x{assemblies_ptr:x}" if assemblies_ptr else "No assemblies")

        # TODO: Walk assemblies to find Core.dll, then find Window class
        # This requires more offset research for MonoLinkedList structure
        # For now, return None and fall back to heuristic scan

        return None


def get_hackmud_pid() -> Optional[int]:
    """Find hackmud process ID"""
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    if 'hackmud' in f.read():
                        return int(pid)
            except:
                pass
    return None


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"Found hackmud PID: {pid}")

    with MonoReaderV2(pid) as reader:
        # Step 1: Find root domain
        root = reader.find_root_domain()
        if root:
            print(f"\nRoot domain: 0x{root:x}")

            # Step 2: Try to find Window vtable
            vtable = reader.find_window_vtable()
            if vtable:
                print(f"Window vtable: 0x{vtable:x}")
            else:
                print("Could not find Window vtable (need more offset research)")
                print("Falling back to heuristic scan...")


if __name__ == '__main__':
    main()

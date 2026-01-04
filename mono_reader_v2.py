#!/usr/bin/env python3
"""Mono memory reader v2 - proper vtable-based approach

Based on:
- https://github.com/wetware-enterprises/scribe/
- https://github.com/AkiraYasha/loki/
- Unity Mono BleedingEdge struct research

This finds hackmud's terminal output by:
1. Finding libmonobdwgc-2.0.so and mono_get_root_domain symbol
2. Walking Mono runtime structures to find Window class
3. Getting vtable address from class
4. Scanning heap for Window instances
5. Following fixed offsets to terminal content
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
    # Unity Mono BleedingEdge offsets (researched for hackmud)
    MONO_DOMAIN_ASSEMBLIES = 0x98  # GSList* domain_assemblies
    MONO_ASSEMBLY_NAME = 0x10      # MonoAssemblyName.name (char*)
    MONO_ASSEMBLY_IMAGE = 0x60     # MonoImage* image
    MONO_IMAGE_NAME = 0x30         # char* name
    MONO_CLASS_NAME = 0x40         # char* name
    MONO_CLASS_NAMESPACE = 0x48    # char* name_space
    MONO_CLASS_RUNTIME_INFO = 0xC8 # MonoClassRuntimeInfo*
    MONO_RUNTIME_INFO_VTABLE = 0x8 # MonoVTable*

    # MonoString offsets
    MONO_STRING_LENGTH = 0x10
    MONO_STRING_DATA = 0x14

    def __init__(self, pid: int):
        self.pid = pid
        self.mem_file = None
        self.mono_base = None
        self.root_domain = None
        self.regions = []

    def __enter__(self):
        self.mem_file = open(f'/proc/{self.pid}/mem', 'rb')
        self.regions = self._get_regions()
        return self

    def __exit__(self, *args):
        if self.mem_file:
            self.mem_file.close()

    def _get_regions(self) -> List[MemoryRegion]:
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

    def is_valid_ptr(self, ptr: int) -> bool:
        """Check if pointer is in a readable region"""
        if ptr < 0x1000 or ptr > 0x7FFFFFFFFFFF:
            return False
        for region in self.regions:
            if region.start <= ptr < region.end and 'r' in region.perms:
                return True
        return False

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
        for region in self.regions:
            if 'libmonobdwgc-2.0.so' in region.path and region.perms.startswith('r-x'):
                return (region.start, region.path)
        return None

    def find_root_domain(self) -> Optional[int]:
        """Find mono root domain via mono_get_root_domain symbol"""
        mono_info = self.find_mono_library()
        if not mono_info:
            return None

        base_addr, path = mono_info
        self.mono_base = base_addr

        # Use readelf to find mono_get_root_domain symbol
        try:
            result = subprocess.run(
                ['readelf', '-s', path],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'mono_get_root_domain' in line and 'FUNC' in line:
                    parts = line.split()
                    sym_value = int(parts[1], 16)
                    func_addr = base_addr + sym_value

                    # Read relative offset from function (RIP-relative addressing)
                    offset_data = self.read_bytes(func_addr + 3, 4)
                    if offset_data:
                        rel_offset = struct.unpack('<i', offset_data)[0]
                        root_domain_ptr = func_addr + 7 + rel_offset
                        root_domain = self.read_ptr(root_domain_ptr)
                        if root_domain:
                            self.root_domain = root_domain
                            return root_domain
                    break
        except Exception:
            pass
        return None

    def walk_gslist(self, head: int) -> List[int]:
        """Walk a GSList and return all data pointers"""
        items = []
        current = head
        seen = set()
        while current and current not in seen and self.is_valid_ptr(current):
            seen.add(current)
            data = self.read_ptr(current)      # GSList.data
            next_ptr = self.read_ptr(current + 8)  # GSList.next
            if data:
                items.append(data)
            current = next_ptr
            if len(items) > 200:
                break
        return items

    def find_assembly(self, name: str) -> Optional[int]:
        """Find an assembly by name"""
        if not self.root_domain:
            self.find_root_domain()
        if not self.root_domain:
            return None

        assemblies_ptr = self.read_ptr(self.root_domain + self.MONO_DOMAIN_ASSEMBLIES)
        if not assemblies_ptr:
            return None

        for asm in self.walk_gslist(assemblies_ptr):
            name_ptr = self.read_ptr(asm + self.MONO_ASSEMBLY_NAME)
            if name_ptr:
                asm_name = self.read_cstring(name_ptr)
                if asm_name and name in asm_name:
                    return asm
        return None

    def find_window_class(self) -> Optional[Tuple[int, int]]:
        """Find hackmud.Window MonoClass and its vtable"""
        if not self.root_domain:
            self.find_root_domain()
        if not self.root_domain:
            return None

        # Get heap region
        heap_region = None
        for region in self.regions:
            if '[heap]' in region.path:
                heap_region = region
                break
        if not heap_region:
            return None

        # Scan heap for MonoClass with name="Window" and namespace="hackmud"
        data = self.read_bytes(heap_region.start, heap_region.size)
        if not data:
            return None

        for off in range(0, len(data) - 0x100, 8):
            addr = heap_region.start + off
            name_ptr = struct.unpack('<Q', data[off+0x40:off+0x48])[0]
            if not self.is_valid_ptr(name_ptr):
                continue

            name = self.read_cstring(name_ptr, 32)
            if name != 'Window':
                continue

            ns_ptr = struct.unpack('<Q', data[off+0x48:off+0x50])[0]
            if not self.is_valid_ptr(ns_ptr):
                continue

            ns = self.read_cstring(ns_ptr, 64)
            if ns != 'hackmud':
                continue

            # Found hackmud.Window class, get vtable
            runtime_info = struct.unpack('<Q', data[off+0xC8:off+0xD0])[0]
            if runtime_info and self.is_valid_ptr(runtime_info):
                vtable = self.read_ptr(runtime_info + 0x8)
                if vtable:
                    return (addr, vtable)

        return None

    def find_window_instances(self, vtable: int) -> List[int]:
        """Find all Window instances by scanning for vtable pointer"""
        instances = []

        # Get heap region
        heap_region = None
        for region in self.regions:
            if '[heap]' in region.path:
                heap_region = region
                break
        if not heap_region:
            return instances

        data = self.read_bytes(heap_region.start, heap_region.size)
        if not data:
            return instances

        vtable_bytes = struct.pack('<Q', vtable)
        pos = 0
        while True:
            pos = data.find(vtable_bytes, pos)
            if pos == -1:
                break
            instances.append(heap_region.start + pos)
            pos += 8

        return instances

    def find_terminal_content(self) -> List[str]:
        """Find terminal content using vtable-based approach"""
        result = self.find_window_class()
        if not result:
            return []

        class_addr, vtable = result
        instances = self.find_window_instances(vtable)

        lines = []
        for inst in instances:
            # Search instance fields for MonoStrings with terminal content
            for off in range(0x10, 0x100, 8):
                ptr = self.read_ptr(inst + off)
                if not ptr or not self.is_valid_ptr(ptr):
                    continue

                # Try as MonoString
                s = self.read_mono_string(ptr)
                if s and len(s) > 20 and ('>>>' in s or '<color' in s):
                    lines.append(s)
                    continue

                # Follow one level deeper
                for off2 in range(0, 0x60, 8):
                    ptr2 = self.read_ptr(ptr + off2)
                    if ptr2 and self.is_valid_ptr(ptr2):
                        s = self.read_mono_string(ptr2)
                        if s and len(s) > 20 and ('>>>' in s or '<color' in s):
                            lines.append(s)

        return lines


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
            print(f"Root domain: 0x{root:x}")

            # Step 2: Find Core assembly
            core = reader.find_assembly("Core")
            if core:
                print(f"Core assembly: 0x{core:x}")

            # Step 3: Find Window class and vtable
            result = reader.find_window_class()
            if result:
                class_addr, vtable = result
                print(f"hackmud.Window class: 0x{class_addr:x}")
                print(f"Window vtable: 0x{vtable:x}")

                # Step 4: Find instances
                instances = reader.find_window_instances(vtable)
                print(f"Found {len(instances)} Window instances")

                # Step 5: Search for terminal content
                content = reader.find_terminal_content()
                if content:
                    print(f"\nFound {len(content)} terminal strings")
                    for i, s in enumerate(content[:5]):
                        # Clean up Unity tags for display
                        s_clean = re.sub(r'<[^>]+>', '', s)[:100]
                        print(f"  [{i}] {s_clean}...")
            else:
                print("Could not find Window class")
        else:
            print("Could not find root domain")


if __name__ == '__main__':
    main()

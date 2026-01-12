#!/usr/bin/env python3
"""Find RectTransform class and explore its structure"""

import struct
import os
import sys
import json
from pathlib import Path

OFFSETS_FILE = Path(__file__).parent / "mono_offsets.json"

def load_offsets():
    if OFFSETS_FILE.exists():
        with open(OFFSETS_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_hackmud_pid():
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                with open(f'/proc/{p}/comm', 'r') as f:
                    if 'hackmud' in f.read():
                        return int(p)
            except:
                pass
    return None

class RectFinder:
    def __init__(self, pid):
        offsets = load_offsets()
        mono = offsets.get('mono_offsets', {})

        self.MONO_CLASS_NAME = int(mono.get('mono_class_name', '0x40'), 16)
        self.MONO_CLASS_NAMESPACE = int(mono.get('mono_class_namespace', '0x48'), 16)
        self.MONO_CLASS_RUNTIME_INFO = int(mono.get('mono_class_runtime_info', '0xC8'), 16)
        self.MONO_RUNTIME_INFO_VTABLE = int(mono.get('mono_runtime_info_vtable', '0x8'), 16)
        self.MONO_STRING_LENGTH = int(mono.get('mono_string_length', '0x10'), 16)
        self.MONO_STRING_DATA = int(mono.get('mono_string_data', '0x14'), 16)

        self.pid = pid
        self.mem = open(f'/proc/{pid}/mem', 'rb')
        self.regions = self._get_regions()
        self.heap_region = self._get_heap()

    def _get_regions(self):
        regions = []
        with open(f'/proc/{self.pid}/maps') as f:
            for line in f:
                if 'rw-p' in line:
                    addrs = line.split()[0].split('-')
                    start = int(addrs[0], 16)
                    end = int(addrs[1], 16)
                    if end - start < 100 * 1024 * 1024:
                        regions.append((start, end))
        return regions

    def _get_heap(self):
        with open(f'/proc/{self.pid}/maps') as f:
            for line in f:
                if '[heap]' in line:
                    addrs = line.split()[0].split('-')
                    return (int(addrs[0], 16), int(addrs[1], 16))
        return None

    def read_ptr(self, addr):
        try:
            self.mem.seek(addr)
            data = self.mem.read(8)
            if len(data) == 8:
                return struct.unpack('<Q', data)[0]
        except:
            pass
        return None

    def read_float(self, addr):
        try:
            self.mem.seek(addr)
            data = self.mem.read(4)
            if len(data) == 4:
                return struct.unpack('<f', data)[0]
        except:
            pass
        return None

    def read_bytes(self, addr, size):
        try:
            self.mem.seek(addr)
            return self.mem.read(size)
        except:
            return None

    def read_cstring(self, addr, max_len=256):
        try:
            self.mem.seek(addr)
            data = self.mem.read(max_len)
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8')
        except:
            return None

    def is_valid(self, ptr):
        return ptr is not None and 0x1000 < ptr < 0x7FFFFFFFFFFF

    def find_class_info(self, class_name, namespace=None):
        """Find class in heap and return class addr and vtable"""
        if not self.heap_region:
            return None, None

        start, end = self.heap_region
        data = self.read_bytes(start, end - start)
        if not data:
            return None, None

        for off in range(0, len(data) - 0x100, 8):
            name_ptr = struct.unpack('<Q', data[off+self.MONO_CLASS_NAME:off+self.MONO_CLASS_NAME+8])[0]
            if not self.is_valid(name_ptr):
                continue

            name = self.read_cstring(name_ptr, 64)
            if name != class_name:
                continue

            if namespace:
                ns_ptr = struct.unpack('<Q', data[off+self.MONO_CLASS_NAMESPACE:off+self.MONO_CLASS_NAMESPACE+8])[0]
                if self.is_valid(ns_ptr):
                    ns = self.read_cstring(ns_ptr, 64)
                    if ns != namespace:
                        continue

            runtime_info = struct.unpack('<Q', data[off+self.MONO_CLASS_RUNTIME_INFO:off+self.MONO_CLASS_RUNTIME_INFO+8])[0]
            if runtime_info and self.is_valid(runtime_info):
                vtable = self.read_ptr(runtime_info + self.MONO_RUNTIME_INFO_VTABLE)
                if vtable:
                    return start + off, vtable

        return None, None

    def find_instances(self, vtable):
        """Find all instances with given vtable"""
        vt_bytes = struct.pack('<Q', vtable)
        instances = []

        for start, end in self.regions:
            data = self.read_bytes(start, end - start)
            if not data:
                continue

            pos = 0
            while True:
                pos = data.find(vt_bytes, pos)
                if pos == -1:
                    break
                instances.append(start + pos)
                pos += 8

        return instances

    def dump_instance_floats(self, addr, count=60):
        """Dump all float values from an instance"""
        print(f"\nInstance at 0x{addr:x}:")
        floats = []
        for off in range(0x10, count * 4, 4):
            f = self.read_float(addr + off)
            if f is not None and abs(f) < 5000 and f != 0:
                floats.append((off, f))

        # Print in groups of 4 (potential Rect structures)
        for i, (off, f) in enumerate(floats):
            if i % 4 == 0 and i > 0:
                print()
            print(f"  +0x{off:03x}: {f:10.2f}", end="")
        print()

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    finder = RectFinder(pid)

    # Search for classes that might have rect info
    classes_to_find = [
        ("RectTransform", "UnityEngine"),
        ("Graphic", "UnityEngine.UI"),
        ("MaskableGraphic", "UnityEngine.UI"),
        ("CanvasRenderer", "UnityEngine"),
        ("Canvas", "UnityEngine"),
    ]

    for class_name, namespace in classes_to_find:
        class_addr, vtable = finder.find_class_info(class_name, namespace)
        if class_addr:
            print(f"\n{'='*60}")
            print(f"Found {namespace}.{class_name}")
            print(f"  Class: 0x{class_addr:x}")
            print(f"  VTable: 0x{vtable:x}")

            instances = finder.find_instances(vtable)
            print(f"  Instances: {len(instances)}")

            # Dump first few instances
            for inst in instances[:3]:
                finder.dump_instance_floats(inst)
        else:
            print(f"Not found: {namespace}.{class_name}")

    finder.close()


if __name__ == '__main__':
    main()

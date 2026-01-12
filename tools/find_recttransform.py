#!/usr/bin/env python3
"""Find RectTransform coordinates by following object references"""

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

class RectTransformFinder:
    def __init__(self, pid):
        offsets = load_offsets()
        mono = offsets.get('mono_offsets', {})
        window = offsets.get('window_offsets', {})

        self.MONO_CLASS_NAME = int(mono.get('mono_class_name', '0x40'), 16)
        self.MONO_CLASS_NAMESPACE = int(mono.get('mono_class_namespace', '0x48'), 16)
        self.MONO_CLASS_RUNTIME_INFO = int(mono.get('mono_class_runtime_info', '0xC8'), 16)
        self.MONO_RUNTIME_INFO_VTABLE = int(mono.get('mono_runtime_info_vtable', '0x8'), 16)
        self.MONO_STRING_LENGTH = int(mono.get('mono_string_length', '0x10'), 16)
        self.MONO_STRING_DATA = int(mono.get('mono_string_data', '0x14'), 16)

        self.WINDOW_NAME = int(window.get('name', '0x90'), 16)
        self.WINDOW_GUI_TEXT = int(window.get('gui_text', '0x58'), 16)

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

    def read_int32(self, addr):
        try:
            self.mem.seek(addr)
            data = self.mem.read(4)
            if len(data) == 4:
                return struct.unpack('<I', data)[0]
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

    def read_mono_string(self, addr, max_chars=100):
        if not addr or addr < 0x1000:
            return None
        length = self.read_int32(addr + self.MONO_STRING_LENGTH)
        if length is None or length < 1 or length > 1000:
            return None
        try:
            data = self.read_bytes(addr + self.MONO_STRING_DATA, min(length * 2, max_chars * 2))
            if not data:
                return None
            return data.decode('utf-16-le', errors='replace')
        except:
            return None

    def is_valid(self, ptr):
        return ptr is not None and 0x1000 < ptr < 0x7FFFFFFFFFFF

    def find_class_vtable(self, class_name, namespace=None):
        """Find vtable for a given class name"""
        if not self.heap_region:
            return None

        start, end = self.heap_region
        data = self.read_bytes(start, end - start)
        if not data:
            return None

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
                    return vtable

        return None

    def find_window_by_name(self, target_name):
        """Find Window instance by name"""
        vtable = self.find_class_vtable('Window', 'hackmud')
        if not vtable:
            return None

        vt_bytes = struct.pack('<Q', vtable)

        for start, end in self.regions:
            data = self.read_bytes(start, end - start)
            if not data:
                continue

            pos = 0
            while True:
                pos = data.find(vt_bytes, pos)
                if pos == -1:
                    break

                window_addr = start + pos
                name_ptr = self.read_ptr(window_addr + self.WINDOW_NAME)
                name = self.read_mono_string(name_ptr, 50) if name_ptr else None

                if name == target_name:
                    return window_addr

                pos += 8

        return None

    def probe_object_for_coords(self, addr, name):
        """Probe an object at addr looking for screen coordinate patterns"""
        print(f"\n=== Probing {name} at 0x{addr:x} ===")

        # Try following pointer chains to find RectTransform data
        # In Unity, the typical chain is:
        # Component -> m_GameObject -> m_Transform (RectTransform)
        # RectTransform has position/size data

        # Common offsets to check for pointer to RectTransform
        rect_offsets = [0x20, 0x28, 0x30, 0x38, 0x40, 0x48]

        for off in rect_offsets:
            ptr = self.read_ptr(addr + off)
            if not self.is_valid(ptr):
                continue

            # Check if this pointer leads to an object with coordinate floats
            # RectTransform typically has: localPosition (x,y,z), sizeDelta (w,h), etc.
            # Looking for patterns like screen-space coordinates

            # Try reading floats starting at common RectTransform data offsets
            # Unity RectTransform native data layout varies, but try common spots
            for float_off in [0x38, 0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x80, 0x90, 0xA0]:
                x = self.read_float(ptr + float_off)
                y = self.read_float(ptr + float_off + 4)
                w = self.read_float(ptr + float_off + 8)
                h = self.read_float(ptr + float_off + 12)

                if x is not None and y is not None and w is not None and h is not None:
                    # Check for reasonable screen coordinate patterns
                    if (10 < abs(w) < 2000 and 10 < abs(h) < 1200 and
                        -2000 < x < 2000 and -2000 < y < 2000):
                        print(f"  ptr at +0x{off:02x} -> 0x{ptr:x}")
                        print(f"    +0x{float_off:02x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def find_all_rects(self, window_name):
        """Find window and look for Rect data"""
        window_addr = self.find_window_by_name(window_name)
        if not window_addr:
            print(f"Window '{window_name}' not found")
            return

        print(f"Window '{window_name}': 0x{window_addr:x}")

        # Get gui_text TMP pointer
        gui_text = self.read_ptr(window_addr + self.WINDOW_GUI_TEXT)
        if gui_text and self.is_valid(gui_text):
            print(f"  gui_text: 0x{gui_text:x}")
            self.probe_object_for_coords(gui_text, "TMP")

        # Probe Window object itself
        self.probe_object_for_coords(window_addr, "Window")

        # Check all pointer fields in Window for RectTransform-like objects
        print("\n=== Window pointer fields ===")
        for off in range(0x10, 0x100, 8):
            ptr = self.read_ptr(window_addr + off)
            if not self.is_valid(ptr):
                continue

            # Try to find screen-space float patterns in this object
            for float_off in range(0x20, 0x120, 4):
                x = self.read_float(ptr + float_off)
                y = self.read_float(ptr + float_off + 4)
                w = self.read_float(ptr + float_off + 8)
                h = self.read_float(ptr + float_off + 12)

                if x is not None and y is not None and w is not None and h is not None:
                    # Very specific pattern: reasonable screen rect
                    if (50 < w < 1500 and 50 < h < 1000 and
                        0 <= x <= 1920 and 0 <= y <= 1080):
                        print(f"\n  Window+0x{off:02x} -> 0x{ptr:x}")
                        print(f"    +0x{float_off:02x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    finder = RectTransformFinder(pid)

    for name in ['chat', 'shell', 'scratch']:
        finder.find_all_rects(name)
        print()

    finder.close()


if __name__ == '__main__':
    main()

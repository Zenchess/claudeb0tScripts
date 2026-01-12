#!/usr/bin/env python3
"""Find native RectTransform data by following cachedPtr from managed objects"""

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

class NativeRectFinder:
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
        vtable = self.find_class_vtable('Window', 'hackmud')
        if not vtable:
            return None, None

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
                    gui_text = self.read_ptr(window_addr + self.WINDOW_GUI_TEXT)
                    return window_addr, gui_text

                pos += 8

        return None, None

    def find_rect_in_native(self, managed_obj_addr, name):
        """Follow cachedPtr from managed object to find native rect data"""
        print(f"\n=== Looking for rect data for {name} ===")
        print(f"Managed object: 0x{managed_obj_addr:x}")

        # In Unity, Component.m_CachedPtr is typically at offset 0x10
        # This points to the native C++ object
        cached_ptr_offsets = [0x10, 0x18, 0x20]

        for ptr_off in cached_ptr_offsets:
            native_ptr = self.read_ptr(managed_obj_addr + ptr_off)
            if not self.is_valid(native_ptr):
                continue

            print(f"\nChecking native ptr at +0x{ptr_off:02x}: 0x{native_ptr:x}")

            # Search for screen-coordinate-like floats in native object
            # RectTransform native data includes: localPosition, sizeDelta, anchoredPosition, rect
            for float_off in range(0x00, 0x200, 4):
                x = self.read_float(native_ptr + float_off)
                y = self.read_float(native_ptr + float_off + 4)
                w = self.read_float(native_ptr + float_off + 8)
                h = self.read_float(native_ptr + float_off + 12)

                if x is None or y is None or w is None or h is None:
                    continue

                # Look for screen-like coordinates
                # Chat window might be around x=1200-1400, y=400-600, w=500-600, h=400-500
                if (0 < w < 2000 and 0 < h < 1200 and
                    -500 < x < 2000 and -500 < y < 1200 and
                    w > 50 and h > 50):
                    print(f"  +0x{float_off:03x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def find_chat_rect(self):
        """Find chat window and extract rect coordinates"""
        window_addr, gui_text = self.find_window_by_name('chat')

        if not window_addr:
            print("Could not find chat window")
            return

        print(f"Chat Window: 0x{window_addr:x}")
        print(f"Chat gui_text: 0x{gui_text:x}" if gui_text else "gui_text: None")

        # The Window object has a RectTransform at offset +0x30 (based on earlier analysis)
        rect_transform = self.read_ptr(window_addr + 0x30)
        if rect_transform and self.is_valid(rect_transform):
            print(f"RectTransform at Window+0x30: 0x{rect_transform:x}")
            self.find_rect_in_native(rect_transform, "chat RectTransform")

        # Also check gui_text for rect data
        if gui_text and self.is_valid(gui_text):
            self.find_rect_in_native(gui_text, "chat TMP")

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    finder = NativeRectFinder(pid)
    finder.find_chat_rect()
    finder.close()


if __name__ == '__main__':
    main()

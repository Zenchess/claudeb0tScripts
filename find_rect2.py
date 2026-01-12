#!/usr/bin/env python3
"""Find chat window RectTransform by extending working VtableReader"""

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
        window = offsets.get('window_offsets', {})
        tmp = offsets.get('tmp_offsets', {})

        self.M_TEXT_OFFSET = int(tmp.get('m_text', '0xc8'), 16)
        self.MONO_STRING_LENGTH = int(mono.get('mono_string_length', '0x10'), 16)
        self.MONO_STRING_DATA = int(mono.get('mono_string_data', '0x14'), 16)
        self.MONO_CLASS_NAME = int(mono.get('mono_class_name', '0x40'), 16)
        self.MONO_CLASS_NAMESPACE = int(mono.get('mono_class_namespace', '0x48'), 16)
        self.MONO_CLASS_RUNTIME_INFO = int(mono.get('mono_class_runtime_info', '0xC8'), 16)
        self.MONO_RUNTIME_INFO_VTABLE = int(mono.get('mono_runtime_info_vtable', '0x8'), 16)
        self.WINDOW_NAME = int(window.get('name', '0x90'), 16)
        self.WINDOW_GUI_TEXT = int(window.get('gui_text', '0x58'), 16)

        self.pid = pid
        self.mem = open(f'/proc/{pid}/mem', 'rb')
        self.regions = self._get_regions()
        self.heap_region = self._get_heap()
        self.window_vtable = None

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

    def is_valid(self, ptr):
        return ptr is not None and 0x1000 < ptr < 0x7FFFFFFFFFFF

    def read_mono_string(self, addr, max_chars=100):
        if not self.is_valid(addr):
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

    def find_window_vtable(self):
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

            name = self.read_cstring(name_ptr, 32)
            if name != 'Window':
                continue

            ns_ptr = struct.unpack('<Q', data[off+self.MONO_CLASS_NAMESPACE:off+self.MONO_CLASS_NAMESPACE+8])[0]
            if not self.is_valid(ns_ptr):
                continue

            ns = self.read_cstring(ns_ptr, 64)
            if ns != 'hackmud':
                continue

            runtime_info = struct.unpack('<Q', data[off+self.MONO_CLASS_RUNTIME_INFO:off+self.MONO_CLASS_RUNTIME_INFO+8])[0]
            if runtime_info and self.is_valid(runtime_info):
                vtable = self.read_ptr(runtime_info + self.MONO_RUNTIME_INFO_VTABLE)
                if vtable:
                    self.window_vtable = vtable
                    return vtable

        return None

    def find_all_windows(self):
        """Find all Window instances and return dict by name"""
        if not self.window_vtable:
            self.find_window_vtable()
        if not self.window_vtable:
            print("Could not find Window vtable")
            return {}

        vt_bytes = struct.pack('<Q', self.window_vtable)
        windows = {}

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

                if name:
                    gui_text = self.read_ptr(window_addr + self.WINDOW_GUI_TEXT)
                    windows[name] = {
                        'window': window_addr,
                        'gui_text': gui_text if self.is_valid(gui_text) else None
                    }

                pos += 8

        return windows

    def explore_window_fields(self, window_addr, name):
        """Explore Window fields for RectTransform-related data"""
        print(f"\n=== Window '{name}' at 0x{window_addr:x} ===")

        # Dump all pointer fields
        print("Pointer fields:")
        for off in range(0x18, 0x100, 8):
            ptr = self.read_ptr(window_addr + off)
            if self.is_valid(ptr):
                # Try to identify what this might be
                vtable_ptr = self.read_ptr(ptr)
                desc = ""
                if vtable_ptr and self.is_valid(vtable_ptr):
                    desc = f" (vtable: 0x{vtable_ptr:x})"
                print(f"  +0x{off:02x}: 0x{ptr:x}{desc}")

                # Look for Rect data in this object
                for float_off in range(0x30, 0xC0, 4):
                    x = self.read_float(ptr + float_off)
                    y = self.read_float(ptr + float_off + 4)
                    w = self.read_float(ptr + float_off + 8)
                    h = self.read_float(ptr + float_off + 12)

                    if (x is not None and y is not None and
                        w is not None and h is not None):
                        # Screen-like rect pattern
                        if (50 < w < 1500 and 50 < h < 1000):
                            print(f"       +0x{float_off:02x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def explore_tmp_for_rect(self, tmp_addr, name):
        """Explore TMP/MaskableGraphic for RectTransform reference"""
        print(f"\n=== TMP '{name}' at 0x{tmp_addr:x} ===")

        # MaskableGraphic has m_RectTransform cached pointer
        # Typically at an offset like 0x20-0x30 in Component subclasses
        print("Checking for m_RectTransform pointer:")

        # In Unity, Component has a reference to its GameObject
        # and there's usually a cached m_RectTransform reference
        for off in [0x18, 0x20, 0x28, 0x30, 0x38, 0x40]:
            ptr = self.read_ptr(tmp_addr + off)
            if not self.is_valid(ptr):
                continue

            # Follow the pointer and look for RectTransform data
            # RectTransform fields include: localPosition, sizeDelta, anchoredPosition
            # These are typically stored as Vector2/Vector3 (floats)

            for float_off in range(0x30, 0x100, 4):
                x = self.read_float(ptr + float_off)
                y = self.read_float(ptr + float_off + 4)
                w = self.read_float(ptr + float_off + 8)
                h = self.read_float(ptr + float_off + 12)

                if (x is not None and y is not None and
                    w is not None and h is not None):
                    # Check for screen coordinate patterns
                    if (20 < w < 2000 and 20 < h < 1200):
                        print(f"  ptr at +0x{off:02x} -> 0x{ptr:x}")
                        print(f"    +0x{float_off:02x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    finder = RectFinder(pid)

    print("Finding all windows...")
    windows = finder.find_all_windows()

    for name, info in sorted(windows.items()):
        window_addr = info['window']
        gui_text = info['gui_text']

        print(f"\n{'='*60}")
        print(f"Window: {name}")
        print(f"  addr: 0x{window_addr:x}")
        print(f"  gui_text: 0x{gui_text:x}" if gui_text else "  gui_text: None")

        finder.explore_window_fields(window_addr, name)

        if gui_text:
            finder.explore_tmp_for_rect(gui_text, name)

    finder.close()


if __name__ == '__main__':
    main()

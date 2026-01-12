#!/usr/bin/env python3
"""Find MaskableGraphic/RectTransform coordinates for chat window"""

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
                    return vtable

        return None

    def find_window_by_name(self, target_name):
        """Find Window instance by name, return (window_addr, gui_text_addr)"""
        vtable = self.find_window_vtable()
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
                    tmp_ptr = self.read_ptr(window_addr + self.WINDOW_GUI_TEXT)
                    return window_addr, tmp_ptr

                pos += 8

        return None, None

    def dump_object_floats(self, addr, name, count=100):
        """Dump float fields from an object looking for coordinates"""
        print(f"\n=== {name} at 0x{addr:x} ===")

        # In Unity, MaskableGraphic inherits from Graphic which inherits from UIBehaviour
        # Common float offsets to check:
        # RectTransform typically has: m_LocalPosition (Vector3), m_LocalRotation (Quaternion),
        # m_LocalScale (Vector3), m_AnchoredPosition (Vector2), m_SizeDelta (Vector2), etc.

        # First, check if this has a cachedRectTransform or similar pointer
        for off in range(0x10, min(0x200, count * 8), 8):
            ptr = self.read_ptr(addr + off)
            if ptr and self.is_valid(ptr):
                # Try to see if this pointer leads to something with float coordinates
                pass

        # Look for float patterns that could be x,y coordinates
        # Screen coords are typically 0-1920 for x, 0-1080 for y, or 0-1 for normalized
        float_candidates = []
        for off in range(0x10, min(0x400, count * 4), 4):
            f = self.read_float(addr + off)
            if f is not None and abs(f) < 5000 and f != 0:
                float_candidates.append((off, f))

        # Group floats that could be Rect (x, y, width, height) or Vector2 pairs
        print("Potential coordinate floats:")
        for off, f in float_candidates[:50]:  # Limit output
            print(f"  +0x{off:03x}: {f:10.2f}")

        # Also look for Rect structures (4 consecutive floats)
        print("\nPotential Rect structures (4 consecutive floats):")
        for i in range(0x10, 0x300, 4):
            floats = []
            for j in range(4):
                f = self.read_float(addr + i + j*4)
                if f is not None:
                    floats.append(f)

            # Check if this looks like reasonable screen coordinates
            if len(floats) == 4:
                x, y, w, h = floats
                # Reasonable screen coordinates
                if (0 <= abs(x) <= 2000 and 0 <= abs(y) <= 1200 and
                    0 < w <= 2000 and 0 < h <= 1200 and
                    w > 10 and h > 10):  # Reasonable size
                    print(f"  +0x{i:03x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    finder = RectFinder(pid)

    # Find chat window
    window_addr, gui_text = finder.find_window_by_name('chat')

    if window_addr:
        print(f"Chat Window: 0x{window_addr:x}")
        print(f"Chat gui_text (TMP): 0x{gui_text:x}" if gui_text else "gui_text: not found")

        if gui_text:
            finder.dump_object_floats(gui_text, "chat TMP/MaskableGraphic")
    else:
        print("Could not find chat window")

    # Also check shell window for comparison
    window_addr, gui_text = finder.find_window_by_name('shell')
    if window_addr and gui_text:
        finder.dump_object_floats(gui_text, "shell TMP/MaskableGraphic")

    finder.close()


if __name__ == '__main__':
    main()

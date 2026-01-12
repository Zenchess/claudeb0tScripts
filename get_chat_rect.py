#!/usr/bin/env python3
"""Get chat window x,y coordinates using the working VtableReader approach"""

import struct
import os
import sys
import json
from pathlib import Path

OFFSETS_FILE = Path(__file__).parent / "memory_scanner/mono_offsets.json"

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

class ChatRectFinder:
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
        """Find hackmud.Window vtable - same as read_vtable.py"""
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

    def find_window_by_name(self, target_name):
        """Find Window instance by name"""
        if not self.window_vtable:
            self.find_window_vtable()
        if not self.window_vtable:
            return None

        vt_bytes = struct.pack('<Q', self.window_vtable)

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

    def explore_window_for_rect(self, window_addr, name):
        """Explore Window object structure looking for rect data"""
        print(f"\n=== {name} Window at 0x{window_addr:x} ===")

        # Dump all pointers and check each for rect-like float data
        for off in range(0x18, 0x100, 8):
            ptr = self.read_ptr(window_addr + off)
            if not self.is_valid(ptr):
                continue

            # Check for m_CachedPtr (native pointer) typically at +0x10 of the referenced object
            native_ptr = self.read_ptr(ptr + 0x10)
            if native_ptr and self.is_valid(native_ptr):
                # Look for screen coordinates in native object
                for float_off in range(0x00, 0x100, 4):
                    x = self.read_float(native_ptr + float_off)
                    y = self.read_float(native_ptr + float_off + 4)
                    w = self.read_float(native_ptr + float_off + 8)
                    h = self.read_float(native_ptr + float_off + 12)

                    if x is None or y is None or w is None or h is None:
                        continue

                    # Screen-like rect: reasonable width/height, x/y could be negative (anchored)
                    if (50 < w < 1500 and 50 < h < 1000):
                        print(f"Window+0x{off:02x} -> 0x{ptr:x} -> native 0x{native_ptr:x}")
                        print(f"  +0x{float_off:02x}: x={x:.1f}, y={y:.1f}, w={w:.1f}, h={h:.1f}")

    def get_chat_coords(self):
        """Get chat window coordinates"""
        window_addr = self.find_window_by_name('chat')
        if not window_addr:
            print("Could not find chat window")

            # Debug: print Window vtable info
            print(f"Window vtable: 0x{self.window_vtable:x}" if self.window_vtable else "No vtable")
            return

        print(f"Found chat Window: 0x{window_addr:x}")
        self.explore_window_for_rect(window_addr, 'chat')

        # Also try shell for comparison
        shell_addr = self.find_window_by_name('shell')
        if shell_addr:
            print(f"\nFound shell Window: 0x{shell_addr:x}")
            self.explore_window_for_rect(shell_addr, 'shell')

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    finder = ChatRectFinder(pid)
    finder.get_chat_coords()
    finder.close()


if __name__ == '__main__':
    main()

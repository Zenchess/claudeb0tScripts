#!/usr/bin/env python3
"""Vtable-based terminal reader for hackmud

Uses Mono runtime structures to find TextMeshProUGUI instances
and read m_text field from discovered offsets.

More reliable than heuristic scanning since it uses proper class vtables.
Loads offsets from mono_offsets.json to support game updates.
"""

import struct
import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List, Tuple, Dict

# Path to offsets file
OFFSETS_FILE = Path(__file__).parent / "mono_offsets.json"


def load_offsets() -> Dict:
    """Load offsets from JSON file"""
    if OFFSETS_FILE.exists():
        with open(OFFSETS_FILE, 'r') as f:
            return json.load(f)
    return {}


def get_hackmud_pid() -> Optional[int]:
    """Find hackmud process ID"""
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                with open(f'/proc/{p}/comm', 'r') as f:
                    if 'hackmud' in f.read():
                        return int(p)
            except:
                pass
    return None


class VtableReader:
    def __init__(self, pid: int):
        # Load offsets from JSON (with defaults)
        offsets = load_offsets()
        mono = offsets.get('mono_offsets', {})
        window = offsets.get('window_offsets', {})
        tmp = offsets.get('tmp_offsets', {})

        # TMP_Text.m_text field offset
        self.M_TEXT_OFFSET = int(tmp.get('m_text', '0xc8'), 16)

        # MonoString offsets
        self.MONO_STRING_LENGTH = int(mono.get('mono_string_length', '0x10'), 16)
        self.MONO_STRING_DATA = int(mono.get('mono_string_data', '0x14'), 16)

        # MonoClass offsets
        self.MONO_CLASS_NAME = int(mono.get('mono_class_name', '0x40'), 16)
        self.MONO_CLASS_NAMESPACE = int(mono.get('mono_class_namespace', '0x48'), 16)
        self.MONO_CLASS_RUNTIME_INFO = int(mono.get('mono_class_runtime_info', '0xC8'), 16)
        self.MONO_RUNTIME_INFO_VTABLE = int(mono.get('mono_runtime_info_vtable', '0x8'), 16)

        # Window class offsets
        self.WINDOW_NAME = int(window.get('name', '0x90'), 16)
        self.WINDOW_GUI_TEXT = int(window.get('gui_text', '0x58'), 16)

        # Store class name info
        class_names = offsets.get('class_names', {})
        self.window_class = class_names.get('window_class', 'Window')
        self.window_namespace = class_names.get('window_namespace', 'hackmud')
        self.tmp_class = class_names.get('tmp_class', 'TextMeshProUGUI')
        self.tmp_namespace = class_names.get('tmp_namespace', 'TMPro')
        self.pid = pid
        self.mem = open(f'/proc/{pid}/mem', 'rb')
        self.regions = self._get_regions()
        self.heap_region = self._get_heap()
        self.vtable = None
        self.window_vtable = None
        self.instances = []
        self.shell_instance = None
        self.chat_instance = None
        self.windows = {}  # name -> (window_addr, tmp_addr)

    def _get_regions(self) -> List[Tuple[int, int]]:
        """Get RW memory regions"""
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

    def _get_heap(self) -> Optional[Tuple[int, int]]:
        """Get heap region"""
        with open(f'/proc/{self.pid}/maps') as f:
            for line in f:
                if '[heap]' in line:
                    addrs = line.split()[0].split('-')
                    return (int(addrs[0], 16), int(addrs[1], 16))
        return None

    def read_ptr(self, addr: int) -> Optional[int]:
        try:
            self.mem.seek(addr)
            data = self.mem.read(8)
            if len(data) == 8:
                return struct.unpack('<Q', data)[0]
        except:
            pass
        return None

    def read_int32(self, addr: int) -> Optional[int]:
        try:
            self.mem.seek(addr)
            data = self.mem.read(4)
            if len(data) == 4:
                return struct.unpack('<I', data)[0]
        except:
            pass
        return None

    def read_bytes(self, addr: int, size: int) -> Optional[bytes]:
        try:
            self.mem.seek(addr)
            return self.mem.read(size)
        except:
            return None

    def read_cstring(self, addr: int, max_len: int = 256) -> Optional[str]:
        try:
            self.mem.seek(addr)
            data = self.mem.read(max_len)
            null_idx = data.index(b'\x00')
            return data[:null_idx].decode('utf-8')
        except:
            return None

    def is_valid(self, ptr: int) -> bool:
        return ptr is not None and 0x1000 < ptr < 0x7FFFFFFFFFFF

    def read_mono_string(self, addr: int, max_chars: int = 50000) -> Optional[str]:
        """Read MonoString from address"""
        if not self.is_valid(addr):
            return None
        length = self.read_int32(addr + self.MONO_STRING_LENGTH)
        if length is None or length < 1 or length > 500000:
            return None
        try:
            data = self.read_bytes(addr + self.MONO_STRING_DATA, min(length * 2, max_chars * 2))
            if not data:
                return None
            return data.decode('utf-16-le', errors='replace')
        except:
            return None

    def find_vtable(self) -> Optional[int]:
        """Find TextMeshProUGUI vtable by scanning heap for MonoClass"""
        if not self.heap_region:
            return None

        start, end = self.heap_region
        data = self.read_bytes(start, end - start)
        if not data:
            return None

        name_off = self.MONO_CLASS_NAME
        ns_off = self.MONO_CLASS_NAMESPACE
        ri_off = self.MONO_CLASS_RUNTIME_INFO
        vt_off = self.MONO_RUNTIME_INFO_VTABLE

        for off in range(0, len(data) - 0x100, 8):
            name_ptr = struct.unpack('<Q', data[off+name_off:off+name_off+8])[0]
            if not self.is_valid(name_ptr):
                continue

            name = self.read_cstring(name_ptr, 32)
            if name != self.tmp_class:
                continue

            ns_ptr = struct.unpack('<Q', data[off+ns_off:off+ns_off+8])[0]
            if not self.is_valid(ns_ptr):
                continue

            ns = self.read_cstring(ns_ptr, 64)
            if ns != self.tmp_namespace:
                continue

            # Found class, get vtable
            runtime_info = struct.unpack('<Q', data[off+ri_off:off+ri_off+8])[0]
            if runtime_info and self.is_valid(runtime_info):
                vtable = self.read_ptr(runtime_info + vt_off)
                if vtable:
                    self.vtable = vtable
                    return vtable

        return None

    def find_instances(self) -> List[int]:
        """Find all TextMeshProUGUI instances"""
        if not self.vtable:
            self.find_vtable()
        if not self.vtable:
            return []

        vt_bytes = struct.pack('<Q', self.vtable)
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

        self.instances = instances
        return instances

    def find_window_vtable(self) -> Optional[int]:
        """Find hackmud.Window vtable"""
        if not self.heap_region:
            return None

        start, end = self.heap_region
        data = self.read_bytes(start, end - start)
        if not data:
            return None

        name_off = self.MONO_CLASS_NAME
        ns_off = self.MONO_CLASS_NAMESPACE
        ri_off = self.MONO_CLASS_RUNTIME_INFO
        vt_off = self.MONO_RUNTIME_INFO_VTABLE

        for off in range(0, len(data) - 0x100, 8):
            name_ptr = struct.unpack('<Q', data[off+name_off:off+name_off+8])[0]
            if not self.is_valid(name_ptr):
                continue

            name = self.read_cstring(name_ptr, 32)
            if name != self.window_class:
                continue

            ns_ptr = struct.unpack('<Q', data[off+ns_off:off+ns_off+8])[0]
            if not self.is_valid(ns_ptr):
                continue

            ns = self.read_cstring(ns_ptr, 64)
            if ns != self.window_namespace:
                continue

            runtime_info = struct.unpack('<Q', data[off+ri_off:off+ri_off+8])[0]
            if runtime_info and self.is_valid(runtime_info):
                vtable = self.read_ptr(runtime_info + vt_off)
                if vtable:
                    self.window_vtable = vtable
                    return vtable

        return None

    def find_windows_by_name(self):
        """Find Window instances and their TMP components by name"""
        if not self.window_vtable:
            self.find_window_vtable()
        if not self.window_vtable:
            return

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

                # Read window name
                name_ptr = self.read_ptr(window_addr + self.WINDOW_NAME)
                name = self.read_mono_string(name_ptr, 50) if name_ptr else None

                if name and name in ['shell', 'chat', 'scratch', 'binlog', 'badge', 'breach', 'binmat', 'version']:
                    # Get TMP instance via gui_text
                    tmp_ptr = self.read_ptr(window_addr + self.WINDOW_GUI_TEXT)
                    if tmp_ptr and self.is_valid(tmp_ptr):
                        self.windows[name] = (window_addr, tmp_ptr)

                pos += 8

    def identify_instances(self):
        """Identify shell and chat instances by Window name or content"""
        # Try Window-based approach first (more reliable)
        if not self.windows:
            self.find_windows_by_name()

        if 'shell' in self.windows:
            _, tmp = self.windows['shell']
            self.shell_instance = tmp

        if 'chat' in self.windows:
            _, tmp = self.windows['chat']
            self.chat_instance = tmp

        # If Window approach worked, we're done
        if self.shell_instance and self.chat_instance:
            return

        # Fall back to content-based scanning
        if not self.instances:
            self.find_instances()

        # Track candidates with content length for fallback
        shell_candidates = []
        chat_candidates = []

        for inst in self.instances:
            ptr = self.read_ptr(inst + self.M_TEXT_OFFSET)
            if not self.is_valid(ptr):
                continue

            length = self.read_int32(ptr + self.MONO_STRING_LENGTH)
            if not length or length < 50:
                continue

            text = self.read_mono_string(ptr, 2000)
            if not text:
                continue

            # Shell has >>> prompt or script output
            if '>>>' in text or ('slots:' in text and 'loaded:' in text):
                self.shell_instance = inst
                break
            # Large text blocks are candidates
            elif length > 500:
                shell_candidates.append((inst, length, text))

        # Find chat by content patterns or largest non-shell text block
        for inst in self.instances:
            if inst == self.shell_instance:
                continue

            ptr = self.read_ptr(inst + self.M_TEXT_OFFSET)
            if not self.is_valid(ptr):
                continue

            length = self.read_int32(ptr + self.MONO_STRING_LENGTH)
            if not length or length < 100:
                continue

            text = self.read_mono_string(ptr, 2000)
            if not text:
                continue

            # Chat patterns: timestamps, :::(message delimiters), channel indicators
            if re.search(r'\d{4} 0000', text) or ':::' in text or 'hackmud' in text.lower():
                chat_candidates.append((inst, length, text))

        # Select largest chat candidate
        if chat_candidates:
            chat_candidates.sort(key=lambda x: x[1], reverse=True)
            self.chat_instance = chat_candidates[0][0]

    def read_shell(self, max_chars: int = 50000) -> Optional[str]:
        """Read shell terminal content"""
        if not self.shell_instance:
            self.identify_instances()
        if not self.shell_instance:
            return None

        ptr = self.read_ptr(self.shell_instance + self.M_TEXT_OFFSET)
        if not self.is_valid(ptr):
            return None

        return self.read_mono_string(ptr, max_chars)

    def read_chat(self, max_chars: int = 50000) -> Optional[str]:
        """Read chat content"""
        if not self.chat_instance:
            self.identify_instances()
        if not self.chat_instance:
            return None

        ptr = self.read_ptr(self.chat_instance + self.M_TEXT_OFFSET)
        if not self.is_valid(ptr):
            return None

        return self.read_mono_string(ptr, max_chars)

    def read_window(self, name: str, max_chars: int = 50000) -> Optional[str]:
        """Read any window by name (badge, breach, scratch, etc.)"""
        if not self.windows:
            self.find_windows_by_name()

        if name not in self.windows:
            return None

        _, tmp_ptr = self.windows[name]
        if not self.is_valid(tmp_ptr):
            return None

        ptr = self.read_ptr(tmp_ptr + self.M_TEXT_OFFSET)
        if not self.is_valid(ptr):
            return None

        return self.read_mono_string(ptr, max_chars)

    def find_version(self) -> Optional[str]:
        """Find game version string by scanning for MonoString with version pattern"""
        # Search memory for MonoStrings matching version pattern (vX.XXX)
        # Match exactly: v followed by digits, dot, and more digits (e.g. v2.016)
        version_pattern = re.compile(r'^v\d+\.\d+$')

        candidates = []
        for start, end in self.regions:
            data = self.read_bytes(start, end - start)
            if not data:
                continue

            # Scan for potential MonoString length fields (small values 5-10)
            for offset in range(0, len(data) - 30, 4):
                length_bytes = data[offset:offset+4]
                if len(length_bytes) < 4:
                    continue
                length = struct.unpack('<I', length_bytes)[0]
                if 5 <= length <= 10:  # Version string length e.g. "v2.016" = 6
                    # Try reading as MonoString (length is at +0x10 from start)
                    string_addr = start + offset - self.MONO_STRING_LENGTH
                    if string_addr > 0:
                        text = self.read_mono_string(string_addr, 20)
                        if text:
                            text = text.strip()
                            # Only accept clean ASCII version strings
                            if version_pattern.match(text) and all(ord(c) < 128 for c in text):
                                candidates.append(text)

        # Return the longest matching version (e.g. v2.016 over v2.4)
        if candidates:
            return max(candidates, key=len)
        return None

    def close(self):
        self.mem.close()


def clean_text(text: str, keep_colors: bool = False) -> str:
    """Remove Unity color tags and filter garbage"""
    if not keep_colors:
        text = re.sub(r'<[^>]+>', '', text)

    # Filter garbage characters
    clean_chars = []
    for c in text:
        if c.isprintable() or c in '\n\r\t':
            clean_chars.append(c)

    return ''.join(clean_chars)


def main():
    parser = argparse.ArgumentParser(description='Read hackmud terminal via vtable')
    parser.add_argument('lines', nargs='?', type=int, default=30, help='Number of lines')
    parser.add_argument('--chat', '-c', action='store_true', help='Read chat instead of shell')
    parser.add_argument('--badge', action='store_true', help='Read badge window')
    parser.add_argument('--breach', action='store_true', help='Read breach window')
    parser.add_argument('--window', '-w', type=str, help='Read any window by name (shell, chat, badge, breach, scratch)')
    parser.add_argument('--version', '-v', action='store_true', help='Get game version')
    parser.add_argument('--colors', action='store_true', help='Keep color tags')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug output')
    parser.add_argument('--list-windows', action='store_true', help='List all found windows')
    args = parser.parse_args()

    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running", file=sys.stderr)
        sys.exit(1)

    reader = VtableReader(pid)

    if args.debug or args.list_windows:
        vtable = reader.find_vtable()
        print(f"vtable: 0x{vtable:x}" if vtable else "vtable: not found", file=sys.stderr)
        instances = reader.find_instances()
        print(f"instances: {len(instances)}", file=sys.stderr)
        reader.identify_instances()
        print(f"shell: 0x{reader.shell_instance:x}" if reader.shell_instance else "shell: not found", file=sys.stderr)
        print(f"chat: 0x{reader.chat_instance:x}" if reader.chat_instance else "chat: not found", file=sys.stderr)
        if reader.windows:
            print(f"windows found: {', '.join(reader.windows.keys())}", file=sys.stderr)
        if args.list_windows:
            reader.close()
            return

    # Handle version lookup
    if args.version:
        version = reader.find_version()
        reader.close()
        if version:
            print(version)
        else:
            print("Could not find version", file=sys.stderr)
            sys.exit(1)
        return

    # Determine which window to read
    if args.window:
        text = reader.read_window(args.window)
    elif args.badge:
        text = reader.read_window('badge')
    elif args.breach:
        text = reader.read_window('breach')
    elif args.chat:
        text = reader.read_chat()
    else:
        text = reader.read_shell()

    reader.close()

    if not text:
        print("Could not read terminal", file=sys.stderr)
        sys.exit(1)

    clean = clean_text(text, keep_colors=args.colors)
    lines = clean.split('\n')

    # Get last N lines
    output_lines = lines[-args.lines:] if len(lines) > args.lines else lines
    print('\n'.join(output_lines))


if __name__ == '__main__':
    main()

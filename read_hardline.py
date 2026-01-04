#!/usr/bin/env python3
"""Read hardline IP from HardlineCoordinator memory

Uses Mono runtime structures to find HardlineCoordinator instance,
read the instructions.m_Text state, and extract the IP when ready.

Based on info from Kaj:
- instructions.m_Text contains state: "LOCATING HARDLINE" when IP is ready
- Private string field contains 12-digit IP
"""

import struct
import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List, Tuple, Dict

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


class HardlineReader:
    def __init__(self, pid: int):
        offsets = load_offsets()
        mono = offsets.get('mono_offsets', {})
        hardline = offsets.get('hardline_offsets', {})

        # Mono string offsets
        self.MONO_STRING_LENGTH = int(mono.get('mono_string_length', '0x10'), 16)
        self.MONO_STRING_DATA = int(mono.get('mono_string_data', '0x14'), 16)

        # MonoClass offsets
        self.MONO_CLASS_NAME = int(mono.get('mono_class_name', '0x40'), 16)
        self.MONO_CLASS_NAMESPACE = int(mono.get('mono_class_namespace', '0x48'), 16)
        self.MONO_CLASS_RUNTIME_INFO = int(mono.get('mono_class_runtime_info', '0xC8'), 16)
        self.MONO_RUNTIME_INFO_VTABLE = int(mono.get('mono_runtime_info_vtable', '0x8'), 16)

        # Unity Text.m_Text offset (different from TMP_Text)
        # Text inherits from MaskableGraphic -> Graphic -> UIBehaviour -> MonoBehaviour
        # m_Text is typically around 0x90-0xB0
        self.TEXT_M_TEXT = int(hardline.get('text_m_text', '0x98'), 16)

        # HardlineCoordinator field offsets
        # Discovered 2026-01-04: IP string at offset 0x80
        self.INSTRUCTIONS_OFFSET = int(hardline.get('instructions', '0x98'), 16)
        self.IP_STRING_OFFSET = int(hardline.get('ip_string', '0x80'), 16)

        self.pid = pid
        self.mem = open(f'/proc/{pid}/mem', 'rb')
        self.regions = self._get_regions()
        self.heap_region = self._get_heap()
        self.vtable = None
        self.instance = None

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

    def read_mono_string(self, addr: int, max_chars: int = 1000) -> Optional[str]:
        """Read MonoString from address"""
        if not self.is_valid(addr):
            return None
        length = self.read_int32(addr + self.MONO_STRING_LENGTH)
        if length is None or length < 1 or length > 10000:
            return None
        try:
            data = self.read_bytes(addr + self.MONO_STRING_DATA, min(length * 2, max_chars * 2))
            if not data:
                return None
            return data.decode('utf-16-le', errors='replace')
        except:
            return None

    def find_vtable(self) -> Optional[int]:
        """Find HardlineCoordinator vtable"""
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
            if name != 'HardlineCoordinator':
                continue

            ns_ptr = struct.unpack('<Q', data[off+ns_off:off+ns_off+8])[0]
            if not self.is_valid(ns_ptr):
                continue

            ns = self.read_cstring(ns_ptr, 64)
            if ns != 'hackmud':
                continue

            # Found class, get vtable
            runtime_info = struct.unpack('<Q', data[off+ri_off:off+ri_off+8])[0]
            if runtime_info and self.is_valid(runtime_info):
                vtable = self.read_ptr(runtime_info + vt_off)
                if vtable:
                    self.vtable = vtable
                    return vtable

        return None

    def find_instance(self) -> Optional[int]:
        """Find HardlineCoordinator instance (prefer high-memory active instance)"""
        if not self.vtable:
            self.find_vtable()
        if not self.vtable:
            return None

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

        # Prefer high-memory instances (active ones)
        # Heap instances (0x2xxx...) are often prefabs/copies
        instances.sort(reverse=True)

        for inst in instances:
            # Verify it has an IP string at the expected offset
            ptr = self.read_ptr(inst + self.IP_STRING_OFFSET)
            if self.is_valid(ptr):
                s = self.read_mono_string(ptr)
                if s and len(s) == 12 and s.isdigit():
                    self.instance = inst
                    return self.instance

        # Fall back to first high-memory instance
        for inst in instances:
            if inst > 0x7f0000000000:
                self.instance = inst
                return self.instance

        # Last resort: any instance
        if instances:
            self.instance = instances[0]
            return self.instance

        return None

    def scan_for_ip_string(self, debug: bool = False) -> Optional[Tuple[int, str]]:
        """Scan HardlineCoordinator instance for 12-digit IP string"""
        if not self.instance:
            self.find_instance()
        if not self.instance:
            return None

        # Scan object fields looking for string references
        # HardlineCoordinator has many fields, scan reasonable range
        for offset in range(0x18, 0x150, 8):
            ptr = self.read_ptr(self.instance + offset)
            if not self.is_valid(ptr):
                continue

            string = self.read_mono_string(ptr)
            if not string:
                continue

            # Check for 12-digit IP pattern
            if re.match(r'^\d{12}$', string):
                if debug:
                    print(f"Found IP at offset 0x{offset:x}: {string}", file=sys.stderr)
                return (offset, string)

        return None

    def scan_for_text_reference(self, debug: bool = False) -> Optional[Tuple[int, str]]:
        """Scan for Unity Text reference containing state text"""
        if not self.instance:
            self.find_instance()
        if not self.instance:
            return None

        state_keywords = ['HARDLINE', 'MAPPING', 'LOCATING', 'CONNECTING', 'WAITING']

        # Scan object fields looking for Text object references
        for offset in range(0x18, 0x150, 8):
            ptr = self.read_ptr(self.instance + offset)
            if not self.is_valid(ptr):
                continue

            # Try reading as Text.m_Text (text object -> m_Text field -> string)
            # Try various common Text.m_Text offsets
            for text_off in [0x98, 0x90, 0xA0, 0xA8, 0xB0]:
                text_ptr = self.read_ptr(ptr + text_off)
                if not self.is_valid(text_ptr):
                    continue

                string = self.read_mono_string(text_ptr)
                if not string:
                    continue

                if any(kw in string.upper() for kw in state_keywords):
                    if debug:
                        print(f"Found state text at offset 0x{offset:x}, text_off 0x{text_off:x}: {string}", file=sys.stderr)
                    return (offset, string)

        return None

    def read_state(self) -> Optional[str]:
        """Read instructions.m_Text state"""
        if not self.instance:
            self.find_instance()
        if not self.instance:
            return None

        # Read instructions field (Text object reference)
        text_obj = self.read_ptr(self.instance + self.INSTRUCTIONS_OFFSET)
        if not self.is_valid(text_obj):
            return None

        # Read m_Text from Text object
        text_ptr = self.read_ptr(text_obj + self.TEXT_M_TEXT)
        if not self.is_valid(text_ptr):
            return None

        return self.read_mono_string(text_ptr)

    def read_ip(self) -> Optional[str]:
        """Read IP string field"""
        if not self.instance:
            self.find_instance()
        if not self.instance:
            return None

        ptr = self.read_ptr(self.instance + self.IP_STRING_OFFSET)
        if not self.is_valid(ptr):
            return None

        string = self.read_mono_string(ptr)
        if string and re.match(r'^\d{12}$', string):
            return string
        return None

    def close(self):
        self.mem.close()


def main():
    parser = argparse.ArgumentParser(description='Read hardline IP from HardlineCoordinator')
    parser.add_argument('--scan', '-s', action='store_true', help='Scan for offsets (discovery mode)')
    parser.add_argument('--state', action='store_true', help='Print state text')
    parser.add_argument('--wait', '-w', action='store_true', help='Wait for LOCATING HARDLINE state')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug output')
    args = parser.parse_args()

    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running", file=sys.stderr)
        sys.exit(1)

    reader = HardlineReader(pid)

    if args.debug:
        vtable = reader.find_vtable()
        print(f"vtable: 0x{vtable:x}" if vtable else "vtable: not found", file=sys.stderr)
        instance = reader.find_instance()
        print(f"instance: 0x{instance:x}" if instance else "instance: not found", file=sys.stderr)

    if args.scan:
        # Discovery mode - find offsets
        print("Scanning for state text...", file=sys.stderr)
        result = reader.scan_for_text_reference(debug=True)
        if result:
            print(f"State text offset: 0x{result[0]:x}", file=sys.stderr)
            print(f"State: {result[1]}")
        else:
            print("State text not found", file=sys.stderr)

        print("\nScanning for IP string...", file=sys.stderr)
        result = reader.scan_for_ip_string(debug=True)
        if result:
            print(f"IP offset: 0x{result[0]:x}", file=sys.stderr)
            print(f"IP: {result[1]}")
        else:
            print("IP string not found (may need to be in LOCATING state)", file=sys.stderr)
    elif args.wait:
        import time
        print("Waiting for LOCATING HARDLINE state...", file=sys.stderr)
        while True:
            state = reader.read_state()
            if state and 'LOCATING' in state.upper():
                ip = reader.read_ip()
                if ip:
                    print(ip)
                    break
            time.sleep(0.1)
    elif args.state:
        state = reader.read_state()
        if state:
            print(state)
        else:
            print("Could not read state", file=sys.stderr)
            sys.exit(1)
    else:
        # Default: try to read IP directly
        ip = reader.read_ip()
        if ip:
            print(ip)
        else:
            # Fall back to scan
            result = reader.scan_for_ip_string()
            if result:
                print(result[1])
            else:
                print("Could not read IP (try --scan or --wait)", file=sys.stderr)
                sys.exit(1)

    reader.close()


if __name__ == '__main__':
    main()

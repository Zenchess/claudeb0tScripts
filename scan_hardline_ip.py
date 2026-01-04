#!/usr/bin/env python3
"""Scan for hardline IP during hardline animation"""

import struct
import os
import sys
import re
import time

def get_hackmud_pid():
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                with open(f'/proc/{p}/comm', 'r') as f:
                    if 'hackmud' in f.read():
                        return int(p)
            except: pass
    return None

class MemScanner:
    def __init__(self, pid):
        self.pid = pid
        self.mem = open(f'/proc/{pid}/mem', 'rb')
        self.instance = None
        self.vtable = None

    def read_ptr(self, addr):
        self.mem.seek(addr)
        return struct.unpack('<Q', self.mem.read(8))[0]

    def read_bytes(self, addr, size):
        self.mem.seek(addr)
        return self.mem.read(size)

    def read_cstring(self, addr, max_len=256):
        try:
            self.mem.seek(addr)
            data = self.mem.read(max_len)
            idx = data.index(b'\x00')
            return data[:idx].decode('utf-8')
        except: return None

    def read_mono_string(self, addr):
        try:
            if addr < 0x1000 or addr > 0x7FFFFFFFFFFF:
                return None
            self.mem.seek(addr + 0x10)
            length = struct.unpack('<I', self.mem.read(4))[0]
            if length < 1 or length > 5000:
                return None
            self.mem.seek(addr + 0x14)
            data = self.mem.read(length * 2)
            return data.decode('utf-16-le', errors='replace')
        except: return None

    def find_instance(self):
        """Find HardlineCoordinator instance"""
        # Find heap
        with open(f'/proc/{self.pid}/maps') as f:
            for line in f:
                if '[heap]' in line:
                    addrs = line.split()[0].split('-')
                    heap_start = int(addrs[0], 16)
                    heap_end = int(addrs[1], 16)
                    break

        heap_data = self.read_bytes(heap_start, heap_end - heap_start)

        # Find vtable
        for off in range(0, len(heap_data) - 0x100, 8):
            name_ptr = struct.unpack('<Q', heap_data[off+0x40:off+0x48])[0]
            if name_ptr < 0x1000 or name_ptr > 0x7FFFFFFFFFFF:
                continue
            name = self.read_cstring(name_ptr, 32)
            if name == 'HardlineCoordinator':
                ns_ptr = struct.unpack('<Q', heap_data[off+0x48:off+0x50])[0]
                ns = self.read_cstring(ns_ptr, 64)
                if ns == 'hackmud':
                    runtime_info = struct.unpack('<Q', heap_data[off+0xC8:off+0xD0])[0]
                    self.vtable = self.read_ptr(runtime_info + 0x8)
                    break

        if not self.vtable:
            return None

        # Get RW regions
        regions = []
        with open(f'/proc/{self.pid}/maps') as f:
            for line in f:
                if 'rw-p' in line:
                    addrs = line.split()[0].split('-')
                    start = int(addrs[0], 16)
                    end = int(addrs[1], 16)
                    if end - start < 100*1024*1024:
                        regions.append((start, end))

        # Find instance
        vt_bytes = struct.pack('<Q', self.vtable)
        for start, end in regions:
            data = self.read_bytes(start, end - start)
            if not data: continue
            pos = data.find(vt_bytes)
            if pos != -1:
                self.instance = start + pos
                return self.instance
        return None

    def scan_for_ip(self):
        """Scan instance fields for 12-digit IP"""
        if not self.instance:
            return None

        # Extended scan range
        for offset in range(0x10, 0x300, 8):
            try:
                ptr = self.read_ptr(self.instance + offset)
                if ptr < 0x1000 or ptr > 0x7FFFFFFFFFFF:
                    continue
                s = self.read_mono_string(ptr)
                if s and re.match(r'^\d{12}$', s):
                    return (offset, s)
            except: pass
        return None

    def scan_all_strings(self):
        """Scan and print all readable strings from instance"""
        if not self.instance:
            return

        found = []
        for offset in range(0x10, 0x300, 8):
            try:
                ptr = self.read_ptr(self.instance + offset)
                if ptr < 0x1000 or ptr > 0x7FFFFFFFFFFF:
                    continue
                s = self.read_mono_string(ptr)
                if s and 0 < len(s) < 100:
                    if all(c.isprintable() or c in '\n\r' for c in s):
                        found.append((offset, 'direct', s))

                # Also check nested pointers (Text objects etc)
                for text_off in [0x90, 0x98, 0xA0, 0xA8, 0xB0, 0xB8, 0xC0, 0xC8]:
                    try:
                        text_ptr = self.read_ptr(ptr + text_off)
                        if text_ptr < 0x1000 or text_ptr > 0x7FFFFFFFFFFF:
                            continue
                        ts = self.read_mono_string(text_ptr)
                        if ts and 0 < len(ts) < 200:
                            if all(c.isprintable() or c in '\n\r' for c in ts):
                                found.append((offset, f'->0x{text_off:x}', ts))
                    except: pass
            except: pass
        return found

    def close(self):
        self.mem.close()


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        sys.exit(1)

    scanner = MemScanner(pid)
    print(f"PID: {pid}", file=sys.stderr)

    inst = scanner.find_instance()
    print(f"Instance: 0x{inst:x}" if inst else "Instance not found", file=sys.stderr)

    if not inst:
        sys.exit(1)

    # Continuous scan mode
    print("Scanning for IP (Ctrl+C to stop)...", file=sys.stderr)
    last_strings = set()

    try:
        while True:
            # Quick IP scan
            result = scanner.scan_for_ip()
            if result:
                print(f"\nFOUND IP at 0x{result[0]:02x}: {result[1]}")
                break

            # Also report new strings we find
            strings = scanner.scan_all_strings()
            if strings:
                new_strings = set((s[0], s[2]) for s in strings) - last_strings
                for offset, _, text in strings:
                    if (offset, text) in new_strings:
                        if 'HARDLINE' in text.upper() or re.match(r'^\d{12}$', text):
                            print(f"0x{offset:02x}: {text}")
                last_strings = set((s[0], s[2]) for s in strings)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped", file=sys.stderr)

    scanner.close()


if __name__ == '__main__':
    main()

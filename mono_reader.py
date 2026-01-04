#!/usr/bin/env python3
"""Experimental Mono memory reader using proper struct approach

Based on:
- https://github.com/wetware-enterprises/scribe/
- https://github.com/AkiraYasha/loki/

This attempts to read hackmud's terminal output by navigating
Mono runtime structures rather than brute-force pattern matching.
"""

import struct
import os
import re
from typing import Optional, Tuple, List
from dataclasses import dataclass

# Mono structure offsets (64-bit Linux)
# These may need adjustment based on Unity/Mono version
MONO_OBJECT_VTABLE_OFFSET = 0x0
MONO_STRING_LENGTH_OFFSET = 0x10
MONO_STRING_DATA_OFFSET = 0x14

@dataclass
class MemoryRegion:
    start: int
    end: int
    perms: str
    path: str

    @property
    def size(self) -> int:
        return self.end - self.start

    @property
    def is_rw_anon(self) -> bool:
        """Check if this is an anonymous read-write region (heap)"""
        return self.perms.startswith('rw') and (not self.path or self.path.startswith('['))

class MonoReader:
    def __init__(self, pid: int):
        self.pid = pid
        self.mem_file = None
        self._regions_cache = None

    def __enter__(self):
        self.mem_file = open(f'/proc/{self.pid}/mem', 'rb')
        return self

    def __exit__(self, *args):
        if self.mem_file:
            self.mem_file.close()

    def get_regions(self) -> List[MemoryRegion]:
        """Get all memory regions from /proc/[pid]/maps"""
        if self._regions_cache:
            return self._regions_cache

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

        self._regions_cache = regions
        return regions

    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """Read bytes from memory at address"""
        # Validate address range (64-bit Linux user space)
        if address < 0 or address > 0x7FFFFFFFFFFF or size < 0:
            return None
        try:
            self.mem_file.seek(address)
            return self.mem_file.read(size)
        except (OSError, IOError, ValueError):
            return None

    def read_ptr(self, address: int) -> Optional[int]:
        """Read a 64-bit pointer from address"""
        data = self.read_bytes(address, 8)
        if data and len(data) == 8:
            return struct.unpack('<Q', data)[0]
        return None

    def read_int32(self, address: int) -> Optional[int]:
        """Read a 32-bit integer from address"""
        data = self.read_bytes(address, 4)
        if data and len(data) == 4:
            return struct.unpack('<I', data)[0]
        return None

    def read_mono_string(self, address: int) -> Optional[str]:
        """Read a Mono string from the given address

        MonoString layout (64-bit):
        - 0x00: vtable pointer (8 bytes)
        - 0x08: sync block (8 bytes)
        - 0x10: length (4 bytes, character count)
        - 0x14: chars (length * 2 bytes, UTF-16LE)
        """
        if not address or address < 0x1000:
            return None

        # Read length
        length = self.read_int32(address + MONO_STRING_LENGTH_OFFSET)
        if length is None or length < 0 or length > 100000:
            return None

        if length == 0:
            return ""

        # Read UTF-16 data
        data = self.read_bytes(address + MONO_STRING_DATA_OFFSET, length * 2)
        if data is None:
            return None

        try:
            return data.decode('utf-16-le')
        except:
            return None

    def find_vtable_instances(self, vtable_addr: int,
                               regions: Optional[List[MemoryRegion]] = None,
                               max_instances: int = 100) -> List[int]:
        """Find all instances with the given vtable address"""
        if regions is None:
            regions = [r for r in self.get_regions() if r.is_rw_anon]

        instances = []
        vtable_bytes = struct.pack('<Q', vtable_addr)

        for region in regions:
            if region.size > 100 * 1024 * 1024:  # Skip huge regions
                continue

            data = self.read_bytes(region.start, region.size)
            if not data:
                continue

            # Scan for vtable pointer at aligned addresses
            for offset in range(0, len(data) - 8, 8):
                if data[offset:offset+8] == vtable_bytes:
                    addr = region.start + offset
                    instances.append(addr)
                    if len(instances) >= max_instances:
                        return instances

        return instances

    def find_string_pattern(self, pattern: str,
                            regions: Optional[List[MemoryRegion]] = None) -> List[Tuple[int, str]]:
        """Find strings matching pattern in memory regions"""
        if regions is None:
            regions = [r for r in self.get_regions() if r.is_rw_anon]

        results = []
        pattern_re = re.compile(pattern)

        for region in regions:
            if region.size > 10 * 1024 * 1024:  # Skip huge regions
                continue

            data = self.read_bytes(region.start, region.size)
            if not data:
                continue

            # Try UTF-16LE decode
            try:
                text = data.decode('utf-16-le', errors='ignore')
            except:
                continue

            # Search for pattern
            for match in pattern_re.finditer(text):
                results.append((region.start, match.group()))

        return results

    def scan_for_mono_strings(self,
                              regions: Optional[List[MemoryRegion]] = None,
                              min_length: int = 10,
                              max_results: int = 1000) -> List[Tuple[int, str]]:
        """Scan memory for valid MonoString objects"""
        if regions is None:
            regions = [r for r in self.get_regions() if r.is_rw_anon]

        results = []

        for region in regions:
            if region.size > 50 * 1024 * 1024:
                continue

            # Sample addresses in region looking for valid MonoString headers
            for addr in range(region.start, region.end - 0x100, 0x10):
                # Try to read as MonoString
                s = self.read_mono_string(addr)
                if s and len(s) >= min_length:
                    # Basic validation - should be mostly printable
                    printable_ratio = sum(1 for c in s if c.isprintable() or c in '\n\r\t') / len(s)
                    if printable_ratio > 0.8:
                        results.append((addr, s))
                        if len(results) >= max_results:
                            return results

        return results


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


def find_terminal_strings(reader: MonoReader) -> List[str]:
    """Find strings that look like terminal output"""
    # Look for patterns common in hackmud terminal
    patterns = [
        r'>>>\s*\w+',  # Shell prompts
        r'LOCK_(?:UNLOCKED|ERROR)',  # Lock messages
        r':::[^:]+:::',  # Chat format
        r'Connection Terminated',  # Breach success
        r'hardline',  # Hardline messages
    ]

    results = []
    for pattern in patterns:
        matches = reader.find_string_pattern(pattern)
        for addr, match in matches[:20]:
            results.append(f"[0x{addr:x}] {match[:100]}")

    return results


def analyze_string_regions(reader: MonoReader) -> None:
    """Analyze memory regions for MonoString objects"""
    print("Scanning for MonoString objects...")

    regions = [r for r in reader.get_regions() if r.is_rw_anon and 100*1024 <= r.size <= 10*1024*1024]
    print(f"Found {len(regions)} candidate regions")

    for region in regions[:10]:
        print(f"\nRegion 0x{region.start:x} - 0x{region.end:x} ({region.size // 1024}KB)")

        # Sample some addresses
        strings_found = 0
        for offset in range(0, min(region.size, 1024*1024), 0x100):
            s = reader.read_mono_string(region.start + offset)
            if s and len(s) > 5:
                # Check if it's game-related
                if any(kw in s for kw in ['LOCK', 'unlock', 'color', 'channel', 'claudeb0t', '>>>']):
                    print(f"  [+0x{offset:x}] {s[:80]}")
                    strings_found += 1
                    if strings_found >= 5:
                        break


def find_recent_output(reader: MonoReader) -> None:
    """Find the most recent terminal output by looking for response patterns"""
    print("\n=== Searching for recent script output ===")

    regions = [r for r in reader.get_regions() if r.is_rw_anon and 100*1024 <= r.size <= 20*1024*1024]

    responses = []
    seen = set()

    # Look for JSON-like responses {r: "..."}
    for region in regions:
        data = reader.read_bytes(region.start, min(region.size, 5*1024*1024))
        if not data:
            continue

        try:
            text = data.decode('utf-16-le', errors='ignore')
        except:
            continue

        # Remove color tags
        text = re.sub(r'<color[^>]*>', '', text)
        text = re.sub(r'</color>', '', text)

        # Find response patterns with timestamp context
        # Look for patterns like {"id":"...","t":1767XXXXXX,"script_name":"...","data":"{...}"}
        for match in re.finditer(r'"t"\s*:\s*(\d{10})[^}]*"data"\s*:\s*"([^"]+)"', text):
            timestamp = int(match.group(1))
            data_content = match.group(2)
            # Unescape
            data_content = data_content.replace('\\n', '\n').replace('\\"', '"')
            # Clean to printable
            clean = ''.join(c for c in data_content if c.isprintable() or c in '\n\r')
            if clean and len(clean) > 10:
                key = clean[:50]
                if key not in seen:
                    seen.add(key)
                    responses.append((timestamp, clean))

        # Also find direct response patterns
        for match in re.finditer(r'r:\s*"([^"]{10,500})"', text):
            content = match.group(1)
            clean = ''.join(c for c in content if c.isprintable() or c in '\n\r')
            if clean and len(clean) > 10:
                if any(kw in clean for kw in ['LOCK', 'unlock', 'breach', 'DATA_CHECK', 'hardline']):
                    key = clean[:50]
                    if key not in seen:
                        seen.add(key)
                        responses.append((0, clean))  # No timestamp

    # Sort by timestamp (newest first) and print
    responses.sort(key=lambda x: x[0], reverse=True)
    for ts, content in responses[:30]:
        if ts > 0:
            print(f"[t:{ts}] {content[:150]}")
        else:
            print(f"Response: {content[:150]}")
        print("---")


def find_linebuffer_instances(reader: MonoReader) -> None:
    """Try to find LineBuffer instances in memory"""
    print("\n=== Searching for LineBuffer class ===")

    regions = [r for r in reader.get_regions() if r.is_rw_anon and 100*1024 <= r.size <= 50*1024*1024]

    for region in regions:
        data = reader.read_bytes(region.start, min(region.size, 10*1024*1024))
        if not data:
            continue

        try:
            text = data.decode('utf-16-le', errors='ignore')
        except:
            continue

        # Look for LineBuffer marker
        if 'LineBuffer' in text:
            print(f"  Found LineBuffer reference in region 0x{region.start:x}")
            # Find the context
            idx = text.find('LineBuffer')
            context = text[max(0, idx-50):idx+100]
            clean = ''.join(c for c in context if c.isprintable())
            print(f"    Context: {clean[:150]}")


def find_queue_arrays(reader: MonoReader) -> None:
    """Look for Queue arrays that might hold terminal lines"""
    print("\n=== Looking for Queue-like structures ===")

    regions = [r for r in reader.get_regions() if r.is_rw_anon and 500*1024 <= r.size <= 10*1024*1024]

    for region in regions[:10]:
        # Read MonoQueue-like structure from various offsets
        for base_offset in range(0, min(region.size, 1024*1024), 0x1000):
            addr = region.start + base_offset

            # Read potential queue header
            array_ptr = reader.read_ptr(addr + 0x10)
            head = reader.read_int32(addr + 0x20)
            tail = reader.read_int32(addr + 0x24)
            size = reader.read_int32(addr + 0x28)

            if array_ptr and head is not None and tail is not None and size is not None:
                # Validate - size should be reasonable
                if 0 < size < 10000 and head < 10000 and tail < 10000:
                    # Try to read from the array
                    if array_ptr > 0x10000:
                        # Read first few elements
                        first_elem = reader.read_ptr(array_ptr + 0x10)  # Skip array header
                        if first_elem and first_elem > 0x10000:
                            # Try to read as MonoString
                            s = reader.read_mono_string(first_elem)
                            if s and len(s) > 5:
                                if any(kw in s for kw in ['>>>', 'LOCK', 'color', 'claudeb0t']):
                                    print(f"  Found queue at 0x{addr:x} with size={size}")
                                    print(f"    First element: {s[:100]}")


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"Found hackmud PID: {pid}")

    with MonoReader(pid) as reader:
        # First, look for recent output
        find_recent_output(reader)

        # Look for LineBuffer
        find_linebuffer_instances(reader)

        # Look for queue structures
        find_queue_arrays(reader)

        # Then scan for terminal-related strings
        print("\n=== Looking for terminal output strings ===")
        results = find_terminal_strings(reader)
        for r in results[:20]:
            print(r)


if __name__ == '__main__':
    main()

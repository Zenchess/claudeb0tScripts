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
    """Look for Queue<string> arrays that might hold terminal lines

    From decompiled Core.dll:
    - NMOPNOICKDJ class has Queue<string> FFAKOMDAHHC
    - Queue<string> uses: _items (array), _head, _tail, _size, _version
    - Standard Queue<T> offsets (may vary):
      0x10: _items (T[] array pointer)
      0x18: _head (int)
      0x1C: _tail (int)
      0x20: _size (int)
      0x24: _version (int)
    """
    print("\n=== Looking for Queue<string> structures ===")

    regions = [r for r in reader.get_regions() if r.is_rw_anon and 100*1024 <= r.size <= 20*1024*1024]
    found_queues = []

    for region in regions[:20]:
        # Scan for potential Queue<string> headers
        for base_offset in range(0, min(region.size, 2*1024*1024), 0x8):
            addr = region.start + base_offset

            # Try different offset layouts for Queue<T>
            for items_offset in [0x10, 0x18, 0x8]:
                array_ptr = reader.read_ptr(addr + items_offset)
                if not array_ptr or array_ptr < 0x10000 or array_ptr > 0x7FFFFFFFFFFF:
                    continue

                # Read queue metadata (try both 32-bit and 64-bit offsets)
                size = reader.read_int32(addr + items_offset + 0x10)
                if size is None or size < 1 or size > 5000:
                    continue

                # Try to read array elements (string pointers)
                # Array header: vtable(8) + length(8) + elements...
                array_len = reader.read_int32(array_ptr + 0x8)
                if array_len is None or array_len < 1 or array_len > 10000:
                    continue

                # Read first few string pointers
                terminal_found = False
                sample_strings = []
                for i in range(min(size, 5)):
                    str_ptr = reader.read_ptr(array_ptr + 0x10 + i * 8)
                    if str_ptr and str_ptr > 0x10000:
                        s = reader.read_mono_string(str_ptr)
                        if s and len(s) > 3:
                            sample_strings.append(s[:50])
                            if any(kw in s for kw in ['>>>', 'LOCK', 'color', 'claudeb0t', '::', 'breach']):
                                terminal_found = True

                if terminal_found and sample_strings:
                    found_queues.append({
                        'addr': addr,
                        'size': size,
                        'samples': sample_strings
                    })

    # Print results
    for q in found_queues[:10]:
        print(f"  Queue at 0x{q['addr']:x} (size={q['size']}):")
        for s in q['samples'][:3]:
            print(f"    {s}")


def find_gui_text_content(reader: MonoReader) -> None:
    """Find TextMeshProUGUI text content (the actual terminal display)

    gui_text stores the rendered terminal as a single large string with:
    - Multiple lines joined by newlines
    - Unity rich text color tags
    - Command prompts like >>>
    """
    print("\n=== Searching for gui_text content (large terminal strings) ===")

    regions = [r for r in reader.get_regions() if r.is_rw_anon and 100*1024 <= r.size <= 50*1024*1024]

    # Look for large MonoStrings containing multiple terminal lines
    found = []

    for region in regions[:30]:
        # Scan for MonoString objects
        for offset in range(0, min(region.size, 5*1024*1024), 0x10):
            addr = region.start + offset
            s = reader.read_mono_string(addr)

            if not s or len(s) < 200:  # gui_text would be large
                continue

            # Check for terminal-like content
            newlines = s.count('\n')
            has_prompt = '>>>' in s
            has_colors = '<color' in s.lower() or 'color=' in s.lower()
            has_terminal_content = any(kw in s for kw in ['claudeb0t', 'LOCK_', '::', 'scripts.', 'sys.'])

            # Score the likelihood this is gui_text
            score = 0
            if newlines > 5: score += 2
            if newlines > 20: score += 2
            if has_prompt: score += 3
            if has_colors: score += 2
            if has_terminal_content: score += 2

            if score >= 5:
                found.append({
                    'addr': addr,
                    'score': score,
                    'length': len(s),
                    'newlines': newlines,
                    'preview': s[:500].replace('\n', '\\n')
                })

    # Sort by score
    found.sort(key=lambda x: x['score'], reverse=True)

    for f in found[:5]:
        print(f"\n[0x{f['addr']:x}] Score={f['score']} Len={f['length']} Lines={f['newlines']}")
        print(f"  Preview: {f['preview'][:200]}...")


def main():
    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running")
        return

    print(f"Found hackmud PID: {pid}")

    with MonoReader(pid) as reader:
        # First, look for recent output
        find_recent_output(reader)

        # Look for gui_text content
        find_gui_text_content(reader)

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

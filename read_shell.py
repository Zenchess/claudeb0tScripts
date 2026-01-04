#!/usr/bin/env python3
"""Read hackmud shell output from memory - improved version focusing on actual shell buffer"""
import re
import sys
import os

def get_pid():
    """Find hackmud PID"""
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    if 'hackmud' in f.read():
                        return int(pid)
            except:
                pass
    return None

def strip_color_tags(text):
    """Remove Unity color tags"""
    return re.sub(r'</?color[^>]*>', '', text)

def find_shell_region(pid):
    """Find the shell output memory region by looking for JSON script results"""
    # Look for a unique shell pattern - JSON with success/run_id (UTF-16 encoded)
    pattern = '{"success"'.encode('utf-16-le')

    regions = []
    with open(f'/proc/{pid}/maps', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and 'rw' in parts[1]:
                addr_range = parts[0].split('-')
                start = int(addr_range[0], 16)
                end = int(addr_range[1], 16)
                # Focus on Mono heap regions
                if end - start < 100*1024*1024:
                    regions.append((start, end))

    # Find regions with JSON output
    shell_regions = []
    with open(f'/proc/{pid}/mem', 'rb') as mem:
        for start, end in regions:
            try:
                mem.seek(start)
                data = mem.read(min(end - start, 20*1024*1024))
                if pattern in data:
                    shell_regions.append((start, end))
            except:
                pass

    return shell_regions

def read_shell(num_lines=20, raw=False):
    """Read recent shell output"""
    pid = get_pid()
    if not pid:
        print("Hackmud not running")
        return

    # Find shell output regions
    regions = find_shell_region(pid)
    if not regions:
        print("Shell buffer not found - try running a command first")
        return

    found_entries = []

    # Pattern for shell entries: timestamp (4 digits) followed by channel/username
    # Format: 1442 n00bz claudeb0t :::message:::
    entry_pattern = re.compile(r'(\d{4})\s+([\w-]+)\s+([\w-]+)\s+:::(.+?):::')

    with open(f'/proc/{pid}/mem', 'rb') as mem:
        for start, end in regions:
            try:
                mem.seek(start)
                data = mem.read(end - start)

                # Decode as UTF-16
                try:
                    decoded = data.decode('utf-16-le', errors='ignore')
                except:
                    continue

                # Clean up
                decoded = strip_color_tags(decoded)

                # Find chat/shell entries
                for match in entry_pattern.finditer(decoded):
                    timestamp = match.group(1)
                    channel = match.group(2)
                    user = match.group(3)
                    msg = match.group(4).strip()

                    if len(msg) > 2:
                        entry = f"[{timestamp}] {channel} {user}: {msg[:150]}"
                        if entry not in [e[1] for e in found_entries]:
                            found_entries.append((int(timestamp), entry))

                # Also find JSON script results
                json_pattern = re.compile(r'\{"success"[^}]+\}')
                for match in json_pattern.finditer(decoded):
                    json_str = match.group()
                    entry = f"[JSON] {json_str[:150]}"
                    if entry not in [e[1] for e in found_entries]:
                        found_entries.append((0, entry))

                # Also find >>> commands
                cmd_pattern = re.compile(r'>>>([\w.{}":\[\],\s#=_-]+)')
                for match in cmd_pattern.finditer(decoded):
                    cmd = match.group(1).strip()
                    if len(cmd) > 3 and 'color' not in cmd.lower():
                        entry = f">>> {cmd[:150]}"
                        if entry not in [e[1] for e in found_entries]:
                            found_entries.append((0, entry))

            except Exception as e:
                if raw:
                    print(f"Error in region {hex(start)}: {e}")
                pass

    # Sort by timestamp (entries with timestamp > 0 first, then by value)
    found_entries.sort(key=lambda x: x[0])

    # Return last N entries
    for _, entry in found_entries[-num_lines:]:
        print(entry)

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    raw = '--raw' in sys.argv
    read_shell(n, raw)

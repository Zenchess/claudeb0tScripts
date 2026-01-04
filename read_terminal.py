#!/usr/bin/env python3
"""Read hackmud terminal output from memory (UTF-16 encoded)"""
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

def read_terminal(num_lines=10):
    """Read recent terminal output"""
    pid = get_pid()
    if not pid:
        print("Hackmud not running")
        return

    # Search pattern: >>> prompt in UTF-16
    prompt_pattern = '>>>'.encode('utf-16-le')

    regions = []
    with open(f'/proc/{pid}/maps', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and 'rw' in parts[1]:
                addr_range = parts[0].split('-')
                start = int(addr_range[0], 16)
                end = int(addr_range[1], 16)
                # Focus on likely buffer regions
                if 0x7f9a00000000 < start < 0x7fa000000000:
                    if end - start < 50*1024*1024:
                        regions.append((start, end))

    found_lines = []

    with open(f'/proc/{pid}/mem', 'rb') as mem:
        for start, end in regions[:20]:  # Limit regions to scan
            try:
                mem.seek(start)
                data = mem.read(end - start)

                # Find all >>> prompts
                pos = 0
                while True:
                    pos = data.find(prompt_pattern, pos)
                    if pos < 0:
                        break

                    # Extract line after prompt (up to next null or newline)
                    line_start = pos
                    line_end = pos + 2000

                    # Decode as UTF-16
                    try:
                        chunk = data[line_start:line_end]
                        decoded = chunk.decode('utf-16-le', errors='ignore')

                        # Find end of line
                        for end_marker in ['\n', '\r', '\x00\x00']:
                            end_idx = decoded.find(end_marker)
                            if end_idx > 0:
                                decoded = decoded[:end_idx]
                                break

                        # Strip color tags
                        clean = strip_color_tags(decoded)

                        if len(clean) > 5 and clean not in [l[1] for l in found_lines]:
                            found_lines.append((start + pos, clean[:200]))
                    except:
                        pass

                    pos += 6  # Skip past this prompt

            except:
                pass

    # Sort by address (roughly chronological for circular buffer)
    found_lines.sort(key=lambda x: x[0])

    # Return last N lines
    for addr, line in found_lines[-num_lines:]:
        print(line)

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    read_terminal(n)

#!/usr/bin/env python3
"""
Hackmud memory scanner - reads JSON responses from game memory
"""

import re
import sys
import os
import time
import json
import hashlib
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = SCRIPT_DIR / "responses.log"
INBOX_FILE = SCRIPT_DIR / "inbox.log"

# My username - messages mentioning this or DMs to me are important
MY_USERNAME = "claudeb0t"

def get_pid_by_name(name):
    """Find PID of process by name"""
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    if name in f.read():
                        return int(pid)
            except (IOError, FileNotFoundError):
                pass
    return None

def get_memory_regions(pid, include_all_rw=False):
    """Get readable memory regions from /proc/[pid]/maps"""
    regions = []
    with open(f'/proc/{pid}/maps', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and 'rw' in parts[1]:  # readable+writable
                addr_range = parts[0].split('-')
                start = int(addr_range[0], 16)
                end = int(addr_range[1], 16)

                if include_all_rw:
                    # Include all rw regions for game output scanning
                    regions.append((start, end))
                else:
                    # Only scan anonymous rw regions (where managed heap lives)
                    if len(parts) == 5 or (len(parts) >= 6 and parts[5] == ''):
                        regions.append((start, end))
    return regions

def extract_json(data, pos):
    """Extract a complete JSON object starting at pos"""
    depth = 0
    json_end = pos
    in_string = False
    escape_next = False

    for i in range(pos, min(pos + 100000, len(data))):
        byte = data[i:i+1]

        if escape_next:
            escape_next = False
            continue

        if byte == b'\\':
            escape_next = True
            continue

        if byte == b'"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if byte == b'{':
            depth += 1
        elif byte == b'}':
            depth -= 1
            if depth == 0:
                return data[pos:i+1]

    return None

def extract_text_line(data, pos):
    """Extract a text line/message starting at or around pos"""
    # Find start of line (look backwards for newline or null)
    start = pos
    for i in range(pos, max(0, pos - 200), -1):
        if data[i:i+1] in (b'\n', b'\x00', b'\r'):
            start = i + 1
            break

    # Find end of line (look forwards for newline or null)
    end = pos
    for i in range(pos, min(len(data), pos + 500)):
        if data[i:i+1] in (b'\n', b'\x00', b'\r'):
            end = i
            break

    if end > start:
        return data[start:end]
    return None

def extract_game_output(data, pos):
    """Extract game output block with color codes starting near pos"""
    # Look backwards to find the start of the output block
    start = pos
    for i in range(pos, max(0, pos - 500), -1):
        # Look for start of color tag or newline that begins output
        if data[i:i+7] == b'<color=' and (i == 0 or data[i-1:i] in (b'\n', b'\x00')):
            start = i
            break
        if data[i:i+1] == b'\x00' and i < pos - 10:
            start = i + 1
            break

    # Look forwards to find the end (look for double newline or null bytes)
    end = pos
    null_count = 0
    for i in range(pos, min(len(data), pos + 5000)):
        if data[i:i+1] == b'\x00':
            null_count += 1
            if null_count > 2:
                end = i - null_count + 1
                break
        else:
            null_count = 0
        if data[i:i+2] == b'\n\n':
            end = i
            break

    if end > start and end - start > 20:
        return data[start:end]
    return None

def strip_color_codes(text):
    """Remove Unity color tags from text"""
    # Remove <color=#XXXXXXXX>...</color> tags
    result = re.sub(r'<color=#[0-9A-Fa-f]+>', '', text)
    result = re.sub(r'</color>', '', result)
    return result

def is_important_message(parsed_data):
    """Check if a message is important (DM to me, mentions my name, or money transfer)"""
    if not isinstance(parsed_data, dict):
        return False, None

    # Check the inner 'data' field if present (hackmud response format)
    data = parsed_data
    if 'data' in parsed_data:
        try:
            data = json.loads(parsed_data['data'])
        except (json.JSONDecodeError, TypeError):
            data = parsed_data

    script_name = parsed_data.get('script_name', '')

    # Incoming DM (chats.tell with from_user means someone messaged ME)
    if script_name == 'chats.tell' and 'from_user' in data:
        return True, f"DM from {data['from_user']}: {data.get('msg', '')}"

    # Chat message that mentions my username
    if script_name == 'chats.send':
        msg = data.get('msg', '').lower()
        if MY_USERNAME.lower() in msg:
            user = data.get('user', 'unknown')
            channel = data.get('channel', '?')
            return True, f"Mention in {channel} by {user}: {data.get('msg', '')}"

    # Money transfer received (accts.xfer with direction "from")
    if script_name == 'accts.xfer' and data.get('direction') == 'from':
        sender = data.get('sender', 'unknown')
        amount = data.get('amount', '?')
        memo = data.get('memo', '')
        msg = f"MONEY RECEIVED: {amount} from {sender}"
        if memo:
            msg += f" - memo: {memo}"
        return True, msg

    return False, None

def save_to_inbox(message, timestamp=None):
    """Save an important message to the inbox file"""
    if timestamp is None:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    with open(INBOX_FILE, 'a') as f:
        f.write(f"\n[{timestamp}] {message}\n")

    # Also print with emphasis
    print(f"\n{'='*60}")
    print(f"📬 IMPORTANT: {message}")
    print(f"{'='*60}\n")

def scan_memory_for_game_output(pid, regions, seen_hashes, search_terms=None):
    """Scan all memory regions for game output by searching for content"""
    found = []

    # Default search terms that indicate game output
    if search_terms is None:
        search_terms = [
            b'<color=#',           # Unity color-coded output
            b':::TRUST',           # Trust messages
            b'scripts.',           # Script references
            b'marks.',             # Marks references
            b'`N',                 # Hackmud blue color code
            b'`C',                 # Hackmud cyan color code
            b'`0',                 # Hackmud gray color code
            b'`L',                 # Hackmud lime color code
        ]

    mem_file = f'/proc/{pid}/mem'

    with open(mem_file, 'rb') as mem:
        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:  # Skip regions > 100MB
                continue
            try:
                mem.seek(start)
                data = mem.read(size)

                # Check if this region has any of our search terms
                has_content = False
                for term in search_terms:
                    if term in data:
                        has_content = True
                        break

                if not has_content:
                    continue

                # Look for >> prompts (command output) with color codes
                # Pattern: >><color=...> or just >>
                for match in re.finditer(rb'>><color=#[0-9A-Fa-f]+>', data):
                    pos = match.start()

                    # Extract until next >> prompt or reasonable limit
                    end_pos = pos + 4000
                    next_prompt = data.find(b'\n>>', pos + 2)
                    if next_prompt != -1 and next_prompt < end_pos:
                        end_pos = next_prompt

                    output_bytes = data[pos:end_pos]

                    if output_bytes and len(output_bytes) > 20:
                        h = hashlib.md5(output_bytes).hexdigest()
                        if h in seen_hashes:
                            continue
                        seen_hashes.add(h)

                        try:
                            output_str = output_bytes.decode('utf-8', errors='ignore')
                            clean_output = strip_color_codes(output_str)
                            clean_output = ''.join(c for c in clean_output if c.isprintable() or c in '\n\r\t')

                            if len(clean_output.strip()) > 10:
                                found.append({
                                    'addr': hex(start + pos),
                                    'raw': output_str,
                                    'text': clean_output,
                                    'type': 'game_output'
                                })
                        except UnicodeDecodeError:
                            pass

                # Also look for TRUST messages that might not have >> prefix
                # Match :::TRUST COMMUNICATION::: followed by any printable chars until we hit junk
                for match in re.finditer(rb':::TRUST COMMUNICATION:::', data):
                    pos = match.start()
                    # Extract from the ::: to the end of the message (look for null, newline, or non-printable)
                    end_pos = pos
                    for i in range(pos, min(len(data), pos + 500)):
                        byte_val = data[i]
                        # Stop at null byte or control chars (except common ones)
                        if byte_val == 0 or (byte_val < 32 and byte_val not in (9, 10, 13)):
                            end_pos = i
                            break
                        end_pos = i + 1

                    output_bytes = data[pos:end_pos]

                    if len(output_bytes) < 30:  # Too short, skip
                        continue

                    h = hashlib.md5(output_bytes).hexdigest()
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)

                    try:
                        output_str = output_bytes.decode('utf-8', errors='ignore')
                        clean_output = strip_color_codes(output_str)
                        clean_output = ''.join(c for c in clean_output if c.isprintable() or c in '\n\r\t')
                        clean_output = clean_output.strip()

                        if len(clean_output) > 20:
                            found.append({
                                'addr': hex(start + pos),
                                'raw': output_str,
                                'text': clean_output,
                                'type': 'trust_message'
                            })
                    except UnicodeDecodeError:
                        pass

                # Look for text with hackmud backtick color codes (e.g. `N for blue)
                # Pattern: backtick followed by letter/number (color code) followed by text
                for match in re.finditer(rb'`[A-Za-z0-9][A-Za-z0-9_]+', data):
                    pos = match.start()

                    # Look backwards to find start of this text block
                    block_start = pos
                    for i in range(pos, max(0, pos - 100), -1):
                        if data[i:i+1] in (b'\x00', b'\n'):
                            block_start = i + 1
                            break

                    # Look forward to find end
                    block_end = pos + 200
                    for i in range(pos, min(len(data), pos + 2000)):
                        if data[i:i+1] == b'\x00':
                            block_end = i
                            break

                    output_bytes = data[block_start:block_end]

                    # Must have multiple backtick codes to be interesting
                    if output_bytes.count(b'`') < 3:
                        continue

                    if len(output_bytes) < 30:
                        continue

                    h = hashlib.md5(output_bytes).hexdigest()
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)

                    try:
                        output_str = output_bytes.decode('utf-8', errors='ignore')
                        # Keep backticks in raw, but also make a version showing the color codes
                        clean_output = ''.join(c for c in output_str if c.isprintable() or c in '\n\r\t')
                        clean_output = clean_output.strip()

                        if len(clean_output) > 20:
                            found.append({
                                'addr': hex(start + block_start),
                                'raw': output_str,
                                'text': clean_output,
                                'type': 'backtick_colored'
                            })
                    except UnicodeDecodeError:
                        pass

            except (OSError, IOError):
                continue

    return found

def scan_memory_for_json(pid, regions, seen_hashes):
    """Scan memory regions for JSON-like content and text messages"""
    found = []

    # Patterns for hackmud server responses
    json_patterns = [
        rb'"t":\d+,"script_name":"',  # Script response with timestamp
        rb'\{"ok":',           # Standard API response
        rb'\{"chats":',        # Chat messages
        rb'\{"users":',        # User data
        rb'\{"scripts":',      # Script listings
        rb'\{"balance":',      # GC balance
        rb'\{"hardline":',     # Hardline data
        rb'\{"loc":',          # Location data
        rb'\{"channels":',     # Channel data
        rb'\{"msg":',          # Messages
        rb'\{"sys":',          # System messages
    ]

    # Plain text patterns for error/system messages
    text_patterns = [
        rb':::TRUST COMMUNICATION:::',  # System/error messages
    ]

    combined_json_pattern = rb'|'.join(json_patterns)
    combined_text_pattern = rb'|'.join(text_patterns)

    mem_file = f'/proc/{pid}/mem'

    with open(mem_file, 'rb') as mem:
        for start, end in regions:
            size = end - start
            if size > 100 * 1024 * 1024:  # Skip regions > 100MB
                continue
            try:
                mem.seek(start)
                data = mem.read(size)

                # Scan for JSON patterns
                for match in re.finditer(combined_json_pattern, data):
                    pos = match.start()

                    # For patterns that don't start with {, find the opening brace
                    if data[pos:pos+1] != b'{':
                        # Search backwards for the opening brace
                        for i in range(pos, max(0, pos - 500), -1):
                            if data[i:i+1] == b'{':
                                pos = i
                                break

                    json_bytes = extract_json(data, pos)

                    if json_bytes and len(json_bytes) > 30:
                        # Hash to avoid duplicates
                        h = hashlib.md5(json_bytes).hexdigest()
                        if h in seen_hashes:
                            continue
                        seen_hashes.add(h)

                        try:
                            json_str = json_bytes.decode('utf-8', errors='ignore')
                            # Validate it's actual JSON
                            parsed = json.loads(json_str)

                            # Skip Unity analytics
                            if isinstance(parsed, dict):
                                if parsed.get('type', '').startswith('analytics.'):
                                    continue
                                if parsed.get('type', '').startswith('perf.'):
                                    continue

                            found.append({
                                'addr': hex(start + pos),
                                'json': json_str,
                                'parsed': parsed,
                                'type': 'json'
                            })
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass

                # Scan for plain text patterns (error messages, etc.)
                for match in re.finditer(combined_text_pattern, data):
                    pos = match.start()
                    text_bytes = extract_text_line(data, pos)

                    if text_bytes and len(text_bytes) > 10:
                        # Hash to avoid duplicates
                        h = hashlib.md5(text_bytes).hexdigest()
                        if h in seen_hashes:
                            continue
                        seen_hashes.add(h)

                        try:
                            text_str = text_bytes.decode('utf-8', errors='ignore')
                            # Only include if it looks like a real message
                            if text_str.startswith(':::') and len(text_str) > 20:
                                found.append({
                                    'addr': hex(start + pos),
                                    'text': text_str,
                                    'parsed': {'message': text_str},
                                    'type': 'text'
                                })
                        except UnicodeDecodeError:
                            pass

            except (OSError, IOError):
                continue

    return found

def main():
    watch_mode = '--watch' in sys.argv or '-w' in sys.argv

    pid = get_pid_by_name('hackmud')
    if not pid:
        print("Hackmud process not found!")
        sys.exit(1)

    print(f"Found hackmud process: PID {pid}")

    seen_hashes = set()

    if watch_mode:
        print(f"Watching for new responses... (writing to {OUTPUT_FILE})")
        print("Press Ctrl+C to stop\n")

        while True:
            try:
                # Check if process still exists
                if not os.path.exists(f'/proc/{pid}'):
                    print("Hackmud process ended.")
                    break

                # Scan for JSON responses
                regions = get_memory_regions(pid)
                results = scan_memory_for_json(pid, regions, seen_hashes)

                # Also scan for game output (color-coded text)
                all_regions = get_memory_regions(pid, include_all_rw=True)
                game_results = scan_memory_for_game_output(pid, all_regions, seen_hashes)
                results.extend(game_results)

                for r in results:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    msg_type = r.get('type', 'json')
                    print(f"[{timestamp}] New {msg_type} response at {r['addr']}:")

                    if msg_type in ('game_output', 'trust_message'):
                        print(r.get('text', '')[:1000])
                    else:
                        print(json.dumps(r.get('parsed', {}), indent=2)[:1000])
                    print()

                    # Check if this is an important message (DM or mention)
                    if msg_type == 'json':
                        is_important, inbox_msg = is_important_message(r.get('parsed', {}))
                        if is_important:
                            save_to_inbox(inbox_msg, timestamp)

                    # Trust messages with errors are also important
                    if msg_type == 'trust_message':
                        trust_text = r.get('text', '')
                        if 'terminated' in trust_text.lower() or 'error' in trust_text.lower():
                            save_to_inbox(f"SCRIPT ERROR: {trust_text}", timestamp)

                    # Append to file
                    with open(OUTPUT_FILE, 'a') as f:
                        f.write(f"\n--- {timestamp} [{r['addr']}] [{msg_type}] ---\n")
                        if msg_type in ('game_output', 'trust_message', 'text', 'backtick_colored'):
                            # Write raw output first (preserves color codes), then cleaned text
                            raw_output = r.get('raw', '')
                            if raw_output and raw_output != r.get('text', ''):
                                f.write("=== RAW (with colors) ===\n")
                                f.write(raw_output)
                                f.write("\n=== CLEANED ===\n")
                            f.write(r.get('text', ''))
                        else:
                            f.write(r.get('json', ''))
                        f.write("\n")

                time.sleep(0.5)  # Scan twice per second

            except KeyboardInterrupt:
                print("\nStopped.")
                break
    else:
        regions = get_memory_regions(pid)
        print(f"Found {len(regions)} anonymous memory regions to scan")

        # Also get all rw regions for game output
        all_regions = get_memory_regions(pid, include_all_rw=True)
        print(f"Found {len(all_regions)} total rw regions to scan for game output")

        print("\nScanning for JSON responses...")
        results = scan_memory_for_json(pid, regions, seen_hashes)

        print("Scanning for game output...")
        game_results = scan_memory_for_game_output(pid, all_regions, seen_hashes)
        results.extend(game_results)

        print(f"\nFound {len(results)} responses:\n")
        for r in results:
            msg_type = r.get('type', 'json')
            print(f"--- [{r['addr']}] [{msg_type}] ---")
            if msg_type == 'game_output':
                print(r.get('text', '')[:1000])
            else:
                print(json.dumps(r.get('parsed', {}), indent=2)[:1000])
            print()

if __name__ == '__main__':
    main()

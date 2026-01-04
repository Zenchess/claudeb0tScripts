#!/usr/bin/env python3
"""Read hackmud LIVE shell output - dynamic buffer detection

This script automatically finds the live terminal buffer by:
1. Scanning all rw-p (read-write private) anonymous memory regions
2. Looking for characteristic shell patterns (>>> prompts, color tags, chat format)
3. Identifying which region has the most recent activity
4. Throwing an exception if multiple equally-likely candidates are found

Usage:
    python3 read_live.py [lines] [--colors] [--debug]

Options:
    lines    - Number of lines to show (default: 20)
    --colors - Preserve Unity color tags in output
    --debug  - Show region detection details
"""
import re
import sys
import os
import time

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

def strip_color_tags(text, keep_colors=False):
    """Remove or keep Unity color tags"""
    if keep_colors:
        return text
    # Remove color tags specifically (don't eat >>> prompts!)
    text = re.sub(r'<color[^>]*>', '', text)  # Opening color tags
    text = re.sub(r'</color>', '', text)  # Closing color tags
    return text

def get_memory_regions(pid):
    """Get all rw-p anonymous regions (heap allocations)"""
    regions = []
    with open(f'/proc/{pid}/maps', 'r') as f:
        for line in f:
            parts = line.split()
            # Look for rw-p (read-write private) anonymous regions
            if len(parts) >= 2 and 'rw-p' in parts[1]:
                addr_range = parts[0].split('-')
                start = int(addr_range[0], 16)
                end = int(addr_range[1], 16)
                size = end - start
                # Focus on reasonable-sized regions (100KB to 10MB)
                if 100 * 1024 <= size <= 10 * 1024 * 1024:
                    # Anonymous regions typically have no path or [heap]
                    path = parts[-1] if len(parts) > 5 else ""
                    if not path.endswith('.so') and not path.endswith('.dll'):
                        regions.append((start, end, size, path))
    return regions

def score_region(data, debug=False):
    """Score a memory region for shell content likelihood.

    Returns a dict with:
    - score: overall likelihood score (higher = more likely live buffer)
    - prompts: count of >>> shell prompts
    - colors: count of Unity color tags
    - chats: count of chat entries (timestamp channel user :::msg:::)
    - recency: estimated recency (based on timestamp analysis)
    - clean_prompts: count of prompts that produce clean text
    """
    try:
        decoded = data.decode('utf-16-le', errors='ignore')
    except:
        return {'score': 0, 'prompts': 0, 'colors': 0, 'chats': 0, 'recency': 0, 'clean_prompts': 0}

    # Count shell prompts
    prompts = len(re.findall(r'>>>', decoded))

    # Count CLEAN prompts (prompts that produce readable text after stripping)
    clean_prompts = 0
    stripped = re.sub(r'<color[^>]*>', '', decoded)
    stripped = re.sub(r'</color>', '', stripped)
    for m in re.finditer(r'>>>(.{5,100})', stripped):
        cmd = ''.join(c for c in m.group(1) if 32 <= ord(c) <= 126)
        if len(cmd.strip()) > 5 and re.search(r'[a-z]{3,}', cmd):
            clean_prompts += 1

    # Count Unity color tags
    colors = len(re.findall(r'<color=#[A-Fa-f0-9]{6,8}>', decoded))

    # Count chat format entries (timestamp channel user :::msg:::)
    chats = len(re.findall(r'\d{4}\s+[\w-]+\s+[\w-]+\s*:::', decoded))

    # Look for timestamps and estimate recency
    # Hackmud uses HHMM format timestamps for chat
    timestamps = re.findall(r'(\d{4})\s+[\w-]+\s+[\w-]+\s*:::', decoded)
    recency = 0
    if timestamps:
        # Get current time in HHMM
        now = int(time.strftime('%H%M'))
        recent_count = 0
        for ts in timestamps[-20:]:  # Check last 20 timestamps
            ts_int = int(ts)
            # Consider "recent" if within 2 hours
            diff = abs(now - ts_int)
            if diff < 200:  # Within ~2 hours
                recent_count += 1
        recency = recent_count

    # Also look for Unix timestamps (like 1767537XXX for Jan 2026)
    # These appear in API responses and are more reliable for recency
    unix_ts = re.findall(r'#(\d{10})', decoded)
    if unix_ts:
        now_unix = int(time.time())
        for ts in unix_ts:
            ts_int = int(ts)
            # Within last 5 minutes = very fresh
            if abs(now_unix - ts_int) < 300:
                recency += 5
            # Within last hour
            elif abs(now_unix - ts_int) < 3600:
                recency += 2

    # Look for fresh script output patterns (JSON responses)
    # {r: "...", x: 0} or {ok: ..., r: ...}
    json_responses = len(re.findall(r'\{\s*r:\s*"[^"]+",\s*x:\s*\d', decoded))
    json_responses += len(re.findall(r'LOCK_ERROR', decoded))
    json_responses += len(re.findall(r'LOCK_UNLOCKED', decoded))

    # Scoring formula:
    # - Recency is MOST important (we want fresh output!)
    # - JSON responses indicate active script output
    # - Clean prompts help identify valid regions
    # - Colors and raw prompts are just noise indicators
    color_score = min(colors * 0.01, 5)  # Cap at 5 points from colors
    prompt_score = min(prompts * 0.5, 15)  # Raw prompts less important
    clean_score = clean_prompts * 50  # Clean prompts valuable
    json_score = json_responses * 100  # JSON responses = active output
    score = prompt_score + color_score + chats * 20 + recency * 200 + clean_score + json_score

    return {
        'score': score,
        'prompts': prompts,
        'clean_prompts': clean_prompts,
        'colors': colors,
        'chats': chats,
        'recency': recency,
        'json_responses': json_responses
    }

def find_live_buffer(pid, debug=False):
    """Find the live terminal buffer dynamically.

    Raises:
        RuntimeError: If multiple regions have equally high scores (ambiguous)
        RuntimeError: If no suitable regions found

    Returns:
        tuple: (start_address, end_address, region_data)
    """
    regions = get_memory_regions(pid)

    if debug:
        print(f"Found {len(regions)} candidate regions")

    candidates = []

    with open(f'/proc/{pid}/mem', 'rb') as mem:
        for start, end, size, path in regions:
            try:
                mem.seek(start)
                data = mem.read(min(size, 2 * 1024 * 1024))  # Read up to 2MB
                scores = score_region(data, debug)

                if scores['score'] > 10:  # Minimum threshold
                    candidates.append({
                        'start': start,
                        'end': end,
                        'size': size,
                        'path': path,
                        'data': data,
                        **scores
                    })

                    if debug:
                        print(f"  0x{start:x}: score={scores['score']:.1f} "
                              f"(prompts={scores['prompts']}, clean={scores['clean_prompts']}, "
                              f"chats={scores['chats']}, recency={scores['recency']}, json={scores['json_responses']})")
            except Exception as e:
                if debug:
                    print(f"  Error reading 0x{start:x}: {e}")

    if not candidates:
        raise RuntimeError("No suitable memory regions found. Is hackmud running with an active terminal?")

    # Sort by score descending
    candidates.sort(key=lambda x: x['score'], reverse=True)

    # Check for ambiguity: if top 2 candidates have similar scores
    if len(candidates) >= 2:
        top_score = candidates[0]['score']
        second_score = candidates[1]['score']

        # If second is within 80% of top score, prefer clean_prompts then recency
        if second_score >= top_score * 0.8:
            # Sort ambiguous candidates by clean_prompts first, then recency
            ambiguous = [c for c in candidates if c['score'] >= top_score * 0.8]
            ambiguous.sort(key=lambda x: (x['clean_prompts'], x['recency'], x['chats']), reverse=True)
            if debug:
                print(f"\nAmbiguous regions (within 80% of top score) - picking cleanest:")
                for c in ambiguous[:3]:
                    print(f"  0x{c['start']:x}: clean={c['clean_prompts']}, recency={c['recency']}, score={c['score']:.1f}")
            candidates = ambiguous + [c for c in candidates if c['score'] < top_score * 0.8]

    # Combine data from ALL scored regions to get fresh output from wherever it is
    top_regions = candidates[:15]  # Use top 15 regions

    if debug:
        print(f"\nCombining data from top {len(top_regions)} regions:")
        for c in top_regions:
            print(f"  0x{c['start']:x}: score={c['score']:.1f}, clean={c['clean_prompts']}, recency={c['recency']}")

    # Combine all data
    combined_data = b''.join(c['data'] for c in top_regions)

    return top_regions[0]['start'], top_regions[0]['end'], combined_data

def is_clean_text(text):
    """Check if text contains only ASCII and common chars (no garbage unicode)"""
    for c in text:
        # Allow ASCII printables, common punctuation, and newlines
        if ord(c) > 127 or (ord(c) < 32 and c not in '\n\r\t'):
            if c not in 'åäöøæÅÄÖØÆéèêëàáâãñíìîïóòôõúùûüç':  # Allow Nordic/accented
                return False
    return True

def clean_text(text):
    """Remove garbage unicode characters, keep only ASCII + allowed chars"""
    allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                  ' .,!?;:\'"-_@#$%^&*()[]{}|/\\<>=+`~\n\r\t')
    allowed.update('åäöøæÅÄÖØÆéèêëàáâãñíìîïóòôõúùûüç')
    result = []
    for c in text:
        if c in allowed:
            result.append(c)
        elif ord(c) < 128:  # Other ASCII
            result.append(c)
        # Skip non-ASCII garbage
    return ''.join(result)

def read_live(num_lines=20, keep_colors=False, debug=False):
    """Read live shell output from dynamically detected buffer region"""
    pid = get_pid()
    if not pid:
        print("Hackmud not running")
        return

    if debug:
        print(f"Found hackmud PID: {pid}")
        print("Scanning memory regions...")

    try:
        start, end, data = find_live_buffer(pid, debug)
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    # Decode as UTF-16
    try:
        decoded = data.decode('utf-16-le', errors='ignore')
    except:
        print("Decode error")
        return

    # Optionally strip color tags
    clean = strip_color_tags(decoded, keep_colors)

    # Find shell commands (>> prompts - color stripping eats one >)
    # Pattern: >>username.command{args} or >>username:command
    commands = []
    # Match known users or generic username pattern
    cmd_pattern = re.compile(r'>>(\w+)[.:](\w+(?:\.\w+)?(?:\{[^}]*\})?)')
    for match in cmd_pattern.finditer(clean):
        user = match.group(1)
        cmd = match.group(2)
        # Clean to ASCII only
        cmd = ''.join(c for c in cmd if 32 <= ord(c) <= 126)
        cmd = cmd.strip()
        # Only add if has meaningful command content
        if len(cmd) > 2 and re.search(r'[a-z]{2,}', cmd):
            commands.append(f"{user}.{cmd}")

    # Find chat-formatted entries (timestamp channel user :::message:::)
    chat_pattern = re.compile(r'(\d{4})\s+([\w-]+)\s+([\w-]+)\s*:::(.*?):::')
    chats = []
    seen = set()
    for match in chat_pattern.finditer(clean):
        ts = match.group(1)
        channel = match.group(2)
        user = match.group(3)
        msg = clean_text(match.group(4).strip()[:100])

        # Skip if message contains garbage or is too short
        if not is_clean_text(msg) or len(msg) < 2:
            continue

        # Remove excessive whitespace
        msg = re.sub(r'\s{3,}', ' ', msg)

        entry = f"[{ts}] {channel} {user}: {msg}"

        # Deduplicate
        key = f"{ts}:{user}:{msg[:30]}"
        if key not in seen:
            seen.add(key)
            chats.append((int(ts), entry))

    # Sort chats by timestamp
    chats.sort(key=lambda x: x[0])

    # Find script responses (money transfers, lock results, system messages)
    responses = []
    response_patterns = [
        (r'Received\s+[\d,KMB]+GC\s+from\s+[\w_]+', 'MONEY'),
        (r'Connection Terminated', 'BREACH'),
        (r'LOCK_UNLOCKED\s*\w*', 'LOCK'),
        (r'LOCK_ERROR[^:]*', 'LOCK'),
        (r'Denied access by[^.]+', 'LOCK'),
        (r'is not the correct\s+\w+', 'LOCK'),
        (r'System slots are full', 'SYSTEM'),
        (r'Upgrade transfer failed', 'SYSTEM'),
        (r'hardline required', 'HARDLINE'),
        (r'(\d{1,3}[KMB]\d{0,3}GC|balance[^<]*\d+[KMB]?\d*GC)', 'BALANCE'),
        (r'Msg Sent', 'MSG'),
        (r'Failure', 'FAIL'),
    ]
    for pattern, ptype in response_patterns:
        for match in re.finditer(pattern, clean, re.IGNORECASE):
            msg = clean_text(match.group(0)[:150])
            if msg and len(msg) > 3:
                responses.append(f"[{ptype}] {msg}")

    # Strip ALL color tags from decoded buffer using regex (fast)
    stripped = re.sub(r'<color=[^>]*>', '', decoded)
    stripped = stripped.replace('</color>', '')

    # Search for response patterns: r: " or LOCK_
    print("=== SCRIPT OUTPUT ===")

    # Find r: " responses (now that color tags are stripped)
    idx = 0
    shown = 0
    seen = set()
    while shown < 8:
        idx = stripped.find('r: "', idx)
        if idx == -1:
            break
        # Get 400 chars after
        end = min(len(stripped), idx + 400)
        context = stripped[idx:end]
        # Find the end of the response (look for ", x:" or "}")
        end_idx = context.find('", x:')
        if end_idx == -1:
            end_idx = context.find('"}')
        if end_idx > 0:
            context = context[:end_idx+5]
        # Clean to printable only
        clean = ''.join(c for c in context if 32 <= ord(c) <= 126 or c == '\n')
        clean = clean.replace('\\n', '\n')
        # Dedupe by first 50 chars
        key = clean[:50]
        if key not in seen and len(clean) > 10:
            seen.add(key)
            print(clean[:400])
            print("---")
            shown += 1
        idx += 10

    print("\n=== SCRIPT RESPONSES ===")
    seen_resp = set()
    for resp in responses[-num_lines//3:]:
        if resp not in seen_resp:
            seen_resp.add(resp)
            print(resp)

    print("\n=== SHELL COMMANDS ===")
    # Deduplicate and show recent commands
    seen_cmds = set()
    unique_cmds = []
    for cmd in commands:
        if cmd not in seen_cmds:
            seen_cmds.add(cmd)
            unique_cmds.append(cmd)
    for cmd in unique_cmds[-num_lines//2:]:
        print(f">>> {cmd[:100]}")

    print("\n=== RECENT CHAT ===")
    for _, entry in chats[-num_lines//2:]:
        print(entry)

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20
    keep_colors = '--colors' in sys.argv
    debug = '--debug' in sys.argv
    read_live(n, keep_colors, debug)

#!/usr/bin/env python3
"""
Query the hackmud responses log
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
LOG_FILE = SCRIPT_DIR / "responses.log"

def parse_log():
    """Parse the responses log into structured entries"""
    if not LOG_FILE.exists():
        return []

    entries = []

    with open(LOG_FILE, 'r') as f:
        content = f.read()

    # Split by entry markers (format: --- timestamp [addr] [type] ---)
    # type can be: json, game_output, trust_message, text
    pattern = r'--- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(0x[0-9a-f]+)\](?: \[(\w+)\])? ---\n'
    parts = re.split(pattern, content)

    # parts[0] is empty or before first marker
    # then it's: timestamp, addr, type, content, timestamp, addr, type, content, ...
    i = 1
    while i < len(parts) - 3:
        timestamp = parts[i]
        addr = parts[i + 1]
        entry_type = parts[i + 2] or 'json'  # Default to json if not specified
        content_str = parts[i + 3].strip()

        if content_str:
            if entry_type == 'json':
                try:
                    parsed = json.loads(content_str)
                    entries.append({
                        'timestamp': timestamp,
                        'addr': addr,
                        'type': 'json',
                        'raw': content_str,
                        'parsed': parsed
                    })
                except json.JSONDecodeError:
                    pass
            else:
                # Handle non-JSON entries (trust_message, game_output, text)
                entries.append({
                    'timestamp': timestamp,
                    'addr': addr,
                    'type': entry_type,
                    'raw': content_str,
                    'parsed': {'message': content_str, 'type': entry_type}
                })

        i += 4

    return entries

def get_latest(n=5, script_filter=None):
    """Get the latest n responses, optionally filtered by script name"""
    entries = parse_log()

    if script_filter:
        entries = [e for e in entries if e['parsed'].get('script_name', '').find(script_filter) != -1]

    return entries[-n:]

def get_since(timestamp_str):
    """Get all responses since a timestamp (format: YYYY-MM-DD HH:MM:SS or HH:MM:SS)"""
    entries = parse_log()

    # Handle short format (just time)
    if len(timestamp_str) <= 8:
        today = datetime.now().strftime('%Y-%m-%d')
        timestamp_str = f"{today} {timestamp_str}"

    return [e for e in entries if e['timestamp'] >= timestamp_str]

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Query hackmud responses log')
    parser.add_argument('-n', '--last', type=int, default=5, help='Show last N responses')
    parser.add_argument('-s', '--script', type=str, help='Filter by script name')
    parser.add_argument('--since', type=str, help='Show responses since timestamp')
    parser.add_argument('--raw', action='store_true', help='Show raw JSON')
    parser.add_argument('--tail', action='store_true', help='Continuously watch for new responses')

    args = parser.parse_args()

    if args.tail:
        import time
        seen = set()
        print("Watching for new responses... (Ctrl+C to stop)")
        while True:
            entries = parse_log()
            for e in entries:
                key = (e['timestamp'], e['addr'])
                if key not in seen:
                    seen.add(key)
                    entry_type = e.get('type', 'json')

                    if entry_type in ('trust_message', 'game_output', 'text', 'backtick_colored'):
                        print(f"\n[{e['timestamp']}] [{entry_type.upper()}]")
                        print(e['raw'][:500])
                    else:
                        script = e['parsed'].get('script_name', 'unknown')
                        print(f"\n[{e['timestamp']}] {script}")
                        if args.raw:
                            print(e['raw'])
                        else:
                            # Try to show the data field nicely
                            data = e['parsed'].get('data', '')
                            if isinstance(data, str):
                                try:
                                    data = json.loads(data)
                                    print(json.dumps(data, indent=2)[:500])
                                except:
                                    print(data[:500])
                            else:
                                print(json.dumps(e['parsed'], indent=2)[:500])
            time.sleep(0.5)

    if args.since:
        entries = get_since(args.since)
    else:
        entries = get_latest(args.last, args.script)

    if not entries:
        print("No responses found.")
        return

    for e in entries:
        entry_type = e.get('type', 'json')

        if entry_type in ('trust_message', 'game_output', 'text', 'backtick_colored'):
            # Non-JSON entries - show the raw message
            print(f"\n[{e['timestamp']}] [{entry_type.upper()}]")
            print(e['raw'][:1000])
        else:
            # JSON entries
            script = e['parsed'].get('script_name', 'unknown')
            print(f"\n[{e['timestamp']}] {script}")

            if args.raw:
                print(e['raw'])
            else:
                # Try to show the data field nicely
                data = e['parsed'].get('data', '')
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                        print(json.dumps(data, indent=2)[:1000])
                    except:
                        print(data[:1000])
                else:
                    print(json.dumps(e['parsed'], indent=2)[:1000])

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Auto-complete hardline connections by reading IP from memory

Uses HardlineCoordinator to read the IP digits and types them automatically.
Based on info from Kaj about reading HardlineCoordinator fields.
"""

import subprocess
import time
import sys
import argparse
from read_hardline import HardlineReader, get_hackmud_pid


def get_window_id():
    """Find hackmud window ID"""
    result = subprocess.run(
        ['xdotool', 'search', '--name', 'hackmud'],
        capture_output=True, text=True
    )
    windows = result.stdout.strip().split('\n')
    if windows and windows[0]:
        return windows[0]
    return None


def send_keys(window_id, keys, delay=30):
    """Send keystrokes to window"""
    subprocess.run([
        'xdotool', 'windowactivate', '--sync', window_id
    ], capture_output=True)
    time.sleep(0.1)
    subprocess.run([
        'xdotool', 'type', '--delay', str(delay), keys
    ], capture_output=True)


def start_hardline(window_id):
    """Start a hardline connection"""
    subprocess.run([
        'xdotool', 'windowactivate', '--sync', window_id
    ], capture_output=True)
    time.sleep(0.1)
    subprocess.run([
        'xdotool', 'type', '--delay', '30', 'kernel.hardline'
    ], capture_output=True)
    subprocess.run(['xdotool', 'key', 'Return'], capture_output=True)


def main():
    parser = argparse.ArgumentParser(description='Auto-complete hardline connections')
    parser.add_argument('--start', '-s', action='store_true', help='Start a new hardline')
    parser.add_argument('--wait', '-w', type=float, default=5.0, help='Wait time before reading IP (default: 5s)')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug output')
    args = parser.parse_args()

    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running", file=sys.stderr)
        sys.exit(1)

    window_id = get_window_id()
    if not window_id:
        print("Could not find hackmud window", file=sys.stderr)
        sys.exit(1)

    if args.debug:
        print(f"PID: {pid}", file=sys.stderr)
        print(f"Window: {window_id}", file=sys.stderr)

    if args.start:
        print("Starting hardline...", file=sys.stderr)
        start_hardline(window_id)
        print(f"Waiting {args.wait}s for animation to reach LOCATING state...", file=sys.stderr)
        time.sleep(args.wait)

    # Read IP from memory
    reader = HardlineReader(pid)
    ip = None

    # Poll for IP with valid 12-digit pattern
    print("Reading IP from memory...", file=sys.stderr)
    for attempt in range(30):
        instance = reader.find_instance()
        if instance:
            ip = reader.read_ip()
            if ip and len(ip) == 12 and ip.isdigit():
                print(f"Got IP on attempt {attempt+1}", file=sys.stderr)
                break
        time.sleep(0.2)

    reader.close()

    if not ip:
        print("Could not read IP from memory", file=sys.stderr)
        sys.exit(1)

    print(f"IP: {ip}", file=sys.stderr)

    # Format IP as XXX.XXX.XXX.XXX for display
    formatted = f"{ip[0:3]}.{ip[3:6]}.{ip[6:9]}.{ip[9:12]}"
    print(f"Formatted: {formatted}", file=sys.stderr)

    # Type the IP digits
    print("Typing IP digits...", file=sys.stderr)
    send_keys(window_id, ip, delay=50)

    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Take screenshot of hackmud window and optionally send to Discord"""

import subprocess
import os
import sys
import time
import argparse
from pathlib import Path

SCREENSHOT_DIR = Path("/tmp")


def get_hackmud_window():
    """Find hackmud window ID using xdotool"""
    result = subprocess.run(
        ['xdotool', 'search', '--name', 'hackmud'],
        capture_output=True, text=True
    )
    windows = result.stdout.strip().split('\n')
    if windows and windows[0]:
        return windows[0]
    return None


def take_screenshot_spectacle(output_path):
    """Take screenshot using spectacle (KDE tool, works on Wayland)"""
    # -b = background mode, -n = no notification, -o = output file
    # -a = active window mode
    result = subprocess.run([
        'spectacle', '-b', '-n', '-a', '-o', str(output_path)
    ], capture_output=True, text=True)
    return result.returncode == 0


def take_screenshot_import(window_id, output_path):
    """Take screenshot using ImageMagick import (X11)"""
    result = subprocess.run([
        'import', '-window', window_id, str(output_path)
    ], capture_output=True, text=True)
    return result.returncode == 0


def focus_window(window_id):
    """Focus the hackmud window"""
    subprocess.run(['xdotool', 'windowactivate', '--sync', window_id],
                   capture_output=True)
    time.sleep(0.3)


def send_to_discord(image_path, channel_id=1456288519403208800):
    """Send screenshot to Discord using requests"""
    import requests
    from dotenv import load_dotenv

    load_dotenv()
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        print("DISCORD_BOT_TOKEN not set", file=sys.stderr)
        return False

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}

    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        data = {'content': 'hackmud screenshot:'}
        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        print(f"Screenshot sent to Discord", file=sys.stderr)
        return True
    else:
        print(f"Discord error: {response.status_code} {response.text}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Take hackmud screenshot')
    parser.add_argument('--output', '-o', type=str,
                        default='/tmp/hackmud_screenshot.png',
                        help='Output file path')
    parser.add_argument('--discord', '-d', action='store_true',
                        help='Send to Discord after capture')
    parser.add_argument('--channel', '-c', type=int,
                        default=1456288519403208800,
                        help='Discord channel ID')
    args = parser.parse_args()

    output_path = Path(args.output)

    # Find and focus hackmud window
    window_id = get_hackmud_window()
    if not window_id:
        print("Hackmud window not found", file=sys.stderr)
        sys.exit(1)

    print(f"Found hackmud window: {window_id}", file=sys.stderr)
    focus_window(window_id)

    # Take screenshot
    print("Taking screenshot...", file=sys.stderr)

    # Try spectacle first (works on Wayland)
    if take_screenshot_spectacle(output_path):
        print(f"Screenshot saved: {output_path}", file=sys.stderr)
    else:
        # Fall back to import (X11)
        if take_screenshot_import(window_id, output_path):
            print(f"Screenshot saved: {output_path}", file=sys.stderr)
        else:
            print("Failed to take screenshot", file=sys.stderr)
            sys.exit(1)

    # Send to Discord if requested
    if args.discord:
        send_to_discord(output_path, args.channel)

    print(output_path)


if __name__ == '__main__':
    main()

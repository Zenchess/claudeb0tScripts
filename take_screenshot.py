#!/usr/bin/env python3
"""Take screenshot of hackmud window and optionally send to Discord"""

import subprocess
import os
import sys
import time
import argparse
from pathlib import Path

SCREENSHOT_DIR = Path("/tmp")

# Region definitions as percentage of window (x%, y%, width%, height%)
# These are approximate and may need tuning based on window size
REGIONS = {
    'chat': (64, 43, 30, 46),      # Right side, chat area (trimmed 2px all sides)
    'scratch': (70, 5, 30, 25),    # Right side, top area (scratch area)
    'terminal': (2, 3, 63, 94),    # Left portion of window (trimmed edges)
    'full': (0, 0, 100, 100),      # Full window
}


def crop_image(input_path, output_path, region_name, scale=130):
    """Crop image to specified region using ImageMagick"""
    if region_name not in REGIONS or region_name == 'full':
        return True  # No cropping needed

    # Get image dimensions
    result = subprocess.run(
        ['identify', '-format', '%w %h', str(input_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False

    width, height = map(int, result.stdout.strip().split())

    # Calculate crop region in pixels
    x_pct, y_pct, w_pct, h_pct = REGIONS[region_name]
    x = int(width * x_pct / 100)
    y = int(height * y_pct / 100)
    w = int(width * w_pct / 100)
    h = int(height * h_pct / 100)

    # Crop and scale using ImageMagick convert
    crop_spec = f"{w}x{h}+{x}+{y}"
    result = subprocess.run(
        ['convert', str(input_path), '-crop', crop_spec, '+repage',
         '-resize', f'{scale}%', str(output_path)],
        capture_output=True, text=True
    )
    return result.returncode == 0


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


MESSAGE_ID_FILE = Path("/tmp/screenshot_message_id.txt")


def send_to_discord(image_path, channel_id=1456288519403208800, edit=False):
    """Send or edit screenshot on Discord using requests"""
    import requests
    from dotenv import load_dotenv

    load_dotenv()
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        print("DISCORD_BOT_TOKEN not set", file=sys.stderr)
        return False

    headers = {"Authorization": f"Bot {token}"}

    # Check if we should edit an existing message
    message_id = None
    if edit and MESSAGE_ID_FILE.exists():
        message_id = MESSAGE_ID_FILE.read_text().strip()
        print(f"Editing message {message_id}", file=sys.stderr)

    if message_id:
        # Delete old message and post new one (Discord doesn't allow editing attachments)
        delete_url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}"
        requests.delete(delete_url, headers=headers)

    # Send new message with screenshot
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        data = {'content': 'hackmud screenshot:'}
        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        # Save message ID for future edits
        new_message_id = response.json().get('id')
        if new_message_id:
            MESSAGE_ID_FILE.write_text(new_message_id)
        print(f"Screenshot sent to Discord (msg: {new_message_id})", file=sys.stderr)
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
    parser.add_argument('--edit', '-e', action='store_true',
                        help='Replace/edit previous screenshot message')
    parser.add_argument('--channel', '-c', type=int,
                        default=1456288519403208800,
                        help='Discord channel ID')
    parser.add_argument('--region', '-r', type=str,
                        choices=['full', 'chat', 'terminal', 'scratch'],
                        default='full',
                        help='Region to capture (full, chat, terminal, scratch)')
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

    # Crop to region if specified
    if args.region != 'full':
        print(f"Cropping to region: {args.region}", file=sys.stderr)
        if crop_image(output_path, output_path, args.region):
            print(f"Cropped to {args.region}", file=sys.stderr)
        else:
            print(f"Failed to crop to {args.region}", file=sys.stderr)

    # Send to Discord if requested
    if args.discord or args.edit:
        send_to_discord(output_path, args.channel, edit=args.edit)

    print(output_path)


if __name__ == '__main__':
    main()

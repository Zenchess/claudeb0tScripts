#!/usr/bin/env python3
"""
Screenshot utility for hackmud windows.
Captures screenshots of specific window regions with calibrated offsets.
"""

import os
import subprocess
import json
import sys
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "screenshot_config.json"

def load_config():
    """Load screenshot configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "shell": {"width": 1247, "height": 1066, "x": 0, "y": 10},
        "chat": {"width": 564, "height": 529, "x": 1249, "y": 10}
    }

def get_hackmud_window_id():
    """Get hackmud window ID using xdotool"""
    try:
        result = subprocess.run(
            ["xdotool", "search", "--name", "hackmud"],
            capture_output=True, text=True, env={**os.environ, "DISPLAY": ":0"}
        )
        window_id = result.stdout.strip().split('\n')[0]
        return window_id if window_id else None
    except Exception as e:
        print(f"Error getting window ID: {e}", file=sys.stderr)
    return None

def take_screenshot(region="shell", output=None):
    """Take a screenshot of specified region"""
    config = load_config()

    if region not in config:
        print(f"Unknown region: {region}")
        print(f"Available: {list(config.keys())}")
        return None

    window_id = get_hackmud_window_id()
    if window_id is None:
        print("Could not find hackmud window")
        return None

    reg = config[region]
    x = reg["x"]
    y = reg["y"]
    width = reg["width"]
    height = reg["height"]

    if output is None:
        output = f"/tmp/hackmud_{region}.png"

    # Capture hackmud window directly using maim
    window_capture = "/tmp/hackmud_window_temp.png"
    subprocess.run([
        "maim", "-i", window_id, window_capture
    ], env={**os.environ, "DISPLAY": ":0"}, capture_output=True)

    # Crop to region within the window
    subprocess.run([
        "magick", window_capture, "-crop", f"{width}x{height}+{x}+{y}",
        "+repage", output
    ], capture_output=True)

    if os.path.exists(output):
        print(f"Screenshot saved: {output} ({width}x{height} at window +{x}+{y})")
        return output
    return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Take hackmud screenshots')
    parser.add_argument('region', nargs='?', default='shell', help='Region to capture: shell, chat')
    parser.add_argument('-o', '--output', help='Output file path')
    args = parser.parse_args()

    take_screenshot(args.region, args.output)

#!/usr/bin/env python3
"""
Send commands to hackmud window using xdotool with window targeting (no focus needed)
"""

import subprocess
import sys
import time

def find_hackmud_window():
    """Find the hackmud window ID"""
    try:
        result = subprocess.run(
            ['xdotool', 'search', '--name', 'hackmud'],
            capture_output=True, text=True
        )
        windows = result.stdout.strip().split('\n')
        if windows and windows[0]:
            return windows[0]
    except Exception as e:
        print(f"Error finding window: {e}")
    return None

def send_command(command, press_enter=True):
    """Send a command to the hackmud window without needing focus"""
    window_id = find_hackmud_window()
    if not window_id:
        print("Hackmud window not found!")
        return False

    try:
        # Type the command directly to the window using xdotool (no focus needed)
        # Use --delay to prevent dropped characters
        subprocess.run(['xdotool', 'type', '--window', window_id, '--delay', '50', command], check=True)

        # Press enter if requested
        if press_enter:
            time.sleep(0.1)
            subprocess.run(['xdotool', 'key', '--window', window_id, 'Return'], check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error sending command: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: send_command.py <command> [--no-enter]")
        print("Example: send_command.py 'sys.status'")
        print("         send_command.py 'test' --no-enter")
        sys.exit(1)

    command = sys.argv[1]
    press_enter = '--no-enter' not in sys.argv

    if send_command(command, press_enter):
        print(f"Sent: {command}" + (" [Enter]" if press_enter else " [no Enter]"))
    else:
        print("Failed to send command")
        sys.exit(1)

if __name__ == '__main__':
    main()

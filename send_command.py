#!/usr/bin/env python3
"""
Send commands to hackmud using xdotool (works with XWayland)
"""

import subprocess
import sys
import time

def get_hackmud_window():
    """Get hackmud window ID using xdotool"""
    try:
        result = subprocess.run(
            ['xdotool', 'search', '--name', 'hackmud'],
            capture_output=True, text=True, check=True
        )
        windows = result.stdout.strip().split('\n')
        if windows and windows[0]:
            return windows[0]
        return None
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        print("xdotool not found!")
        return None

def send_command(command, press_enter=True):
    """Send a command to hackmud using xdotool (no focus stealing)"""
    window_id = get_hackmud_window()
    if not window_id:
        print("Could not find hackmud window!")
        return False
    
    try:
        # Send Escape first to clear any existing input
        subprocess.run(['xdotool', 'key', '--window', window_id, 'Escape'], check=True)
        time.sleep(0.02)

        # Type the command
        subprocess.run(['xdotool', 'type', '--window', window_id, '--delay', '10', command], check=True)

        # Press enter if requested
        if press_enter:
            time.sleep(0.05)
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

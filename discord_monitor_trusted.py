#!/usr/bin/env python3
"""Monitor trusted-only Discord channel and post updates"""

import subprocess
import time
import os
import json
from datetime import datetime

TRUSTED_CHANNEL = 1460773738910974034
LAST_CHECK_FILE = "/tmp/discord_trusted_check.json"

def get_last_timestamp():
    """Get the last timestamp we checked"""
    if os.path.exists(LAST_CHECK_FILE):
        try:
            with open(LAST_CHECK_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_timestamp')
        except:
            pass
    return None

def save_timestamp(timestamp):
    """Save the last timestamp we saw"""
    with open(LAST_CHECK_FILE, 'w') as f:
        json.dump({'last_timestamp': timestamp}, f)

def send_to_discord(message):
    """Send message to trusted-only channel"""
    cmd = [
        './discord_venv/bin/python',
        'discord_tools/discord_send_api.py',
        str(TRUSTED_CHANNEL),
        message
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=10)
    except:
        pass

def fetch_messages():
    """Fetch recent messages"""
    cmd = [
        './discord_venv/bin/python',
        'discord_tools/discord_fetch.py',
        '-n', '100'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    except:
        return ""

def main():
    print("Starting trusted-only channel monitor...")
    send_to_discord("🔍 **Monitoring resumed** - ready to respond to messages")

    consecutive_quiet = 0

    while True:
        try:
            output = fetch_messages()

            # Look for messages from trusted users
            has_trusted_message = False
            lines = output.split('\n')

            for line in lines:
                # Check for messages from Kaj (isinctorp), Dunce (stoneboosters), Zenchess
                if ('isinctorp/Kaj' in line or 'stoneboosters/dunce' in line or 'zenchess/Zenchess' in line):
                    if 'claude:' in line:
                        has_trusted_message = True
                        print(f"[{datetime.now()}] Task detected: {line}")

            if has_trusted_message:
                consecutive_quiet = 0
                # Post status
                send_to_discord("✅ **Activity detected** - checking messages and responding")
            else:
                consecutive_quiet += 1
                if consecutive_quiet % 6 == 0:  # Every ~3 minutes
                    print(f"[{datetime.now()}] Still monitoring...")

            time.sleep(30)

        except KeyboardInterrupt:
            send_to_discord("⏹️ **Monitor stopped**")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()

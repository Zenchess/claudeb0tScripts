#!/usr/bin/env python3
"""Continuous Discord monitoring for trusted-only channel"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

TRUSTED_CHANNEL = 1460773738910974034
STATE_FILE = Path("/tmp/discord_monitor_state.json")

def load_state():
    """Load last seen message timestamp"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"last_timestamp": "2026-01-01T00:00:00"}

def save_state(state):
    """Save state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def fetch_messages(limit=50):
    """Fetch recent messages from Discord"""
    cmd = [
        './discord_venv/bin/python',
        'discord_tools/discord_fetch.py',
        '-n', str(limit)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout if result.returncode == 0 else ""
    except:
        return ""

def send_message(text):
    """Send message to trusted-only channel"""
    cmd = [
        './discord_venv/bin/python',
        'discord_tools/discord_send_api.py',
        str(TRUSTED_CHANNEL),
        text
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.returncode == 0
    except:
        return False

def parse_messages(output):
    """Parse Discord message output"""
    messages = []
    for line in output.strip().split('\n'):
        if not line or '===' in line:
            continue
        # Format: [timestamp] userid/username/displayname -> "message"
        try:
            if ' -> ' in line:
                messages.append(line)
        except:
            pass
    return messages

def main():
    print("🚀 Starting continuous Discord monitor...")
    send_message("🟢 **Monitor online** - Continuously watching trusted-only channel")

    state = load_state()
    check_count = 0
    quiet_count = 0

    while True:
        try:
            check_count += 1

            # Fetch messages
            output = fetch_messages(100)
            messages = parse_messages(output)

            if not messages:
                quiet_count += 1
                if quiet_count % 10 == 0:  # Every 5 minutes
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still watching... ({check_count} checks, {quiet_count*30}s quiet)")
                time.sleep(30)
                continue

            quiet_count = 0

            # Check for new messages with tasks
            trusted_users = ['isinctorp', 'stoneboosters', 'zenchess']
            new_tasks = []

            for msg in messages:
                # Look for "claude:" commands
                if 'claude:' in msg.lower():
                    for user in trusted_users:
                        if user in msg:
                            new_tasks.append(msg)
                            break

            if new_tasks:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(new_tasks)} task(s):")
                for task in new_tasks[-5:]:  # Show last 5
                    print(f"  {task}")
                send_message(f"✅ **Activity detected** - Found {len(new_tasks)} task(s), processing...")

            time.sleep(30)

        except KeyboardInterrupt:
            print("\n⏹️ Monitor stopped by user")
            send_message("⏹️ **Monitor stopped**")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()

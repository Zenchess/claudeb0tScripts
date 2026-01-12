#!/usr/bin/env python3
"""
Discord monitoring loop - executes commands from kaj/zenchess/dunce
"""

import subprocess
import time
import json
import os

TRUSTED_USERS = ['zenchess', 'kaj', 'dunce']
CHECK_INTERVAL = 10  # seconds
LAST_MESSAGE_FILE = '/tmp/last_discord_message_id.txt'

def get_last_checked_time():
    """Get the last message timestamp we checked"""
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_checked_time(timestamp):
    """Save the last message timestamp"""
    with open(LAST_MESSAGE_FILE, 'w') as f:
        f.write(timestamp)

def fetch_discord_messages(n=20):
    """Fetch recent Discord messages"""
    try:
        result = subprocess.run(
            ['./discord_venv/bin/python', 'discord_fetch.py', '-n', str(n)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return ""

def parse_messages(output):
    """Parse Discord messages from fetch output"""
    messages = []
    for line in output.split('\n'):
        if line.startswith('['):
            # Format: [timestamp] username: message
            try:
                parts = line.split('] ', 1)
                if len(parts) == 2:
                    timestamp = parts[0][1:]  # Remove leading [
                    rest = parts[1].split(': ', 1)
                    if len(rest) == 2:
                        username = rest[0]
                        message = rest[1]
                        messages.append({
                            'timestamp': timestamp,
                            'username': username,
                            'message': message
                        })
            except:
                continue
    return messages

def send_discord_message(channel_id, message):
    """Send message to Discord"""
    try:
        subprocess.run(
            ['./discord_venv/bin/python', 'discord_send_api.py', channel_id, message],
            timeout=10
        )
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("Starting Discord monitoring loop...")
    print(f"Listening for commands from: {', '.join(TRUSTED_USERS)}")

    last_checked = get_last_checked_time()

    while True:
        try:
            # Fetch messages
            output = fetch_discord_messages(20)
            messages = parse_messages(output)

            # Process new messages from trusted users
            for msg in messages:
                # Skip if we've already processed this timestamp
                if last_checked and msg['timestamp'] <= last_checked:
                    continue

                username = msg['username']
                message = msg['message']

                # Only process commands from trusted users
                if username not in TRUSTED_USERS:
                    continue

                print(f"\n[{msg['timestamp']}] {username}: {message}")

                # Check for commands
                if message.startswith('!'):
                    # Bot command - let the bot handle it
                    print("  -> Bot command, letting discord_bot handle it")
                elif message.lower().startswith('claude'):
                    # Direct command to me
                    print(f"  -> Command from {username}: {message}")
                    send_discord_message('1456288519403208800', f"Received: {message}")

                # Update last checked timestamp
                last_checked = msg['timestamp']
                save_last_checked_time(last_checked)

            # Wait before next check
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\nStopping Discord monitor...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()

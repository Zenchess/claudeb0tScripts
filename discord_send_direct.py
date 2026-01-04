#!/usr/bin/env python3
"""Send Discord message directly (no queue/bot process needed)"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = 1456288519403208800  # Default channel

def send_message(content, channel_id=CHANNEL_ID):
    """Send message directly via Discord API"""
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not set", file=sys.stderr)
        return False

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    data = {"content": content}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print(f"Sent: {content[:50]}...")
        return True
    else:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: discord_send_direct.py <message> [channel_id]")
        sys.exit(1)

    message = sys.argv[1]
    channel = int(sys.argv[2]) if len(sys.argv) > 2 else CHANNEL_ID

    success = send_message(message, channel)
    sys.exit(0 if success else 1)

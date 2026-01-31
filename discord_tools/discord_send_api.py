#!/usr/bin/env python3
"""Send Discord messages directly via API (no bot required)"""
import argparse
import requests
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"
DEFAULT_CHANNEL = "1456288519403208800"  # general channel

def load_token():
    with open(ENV_FILE) as f:
        for line in f:
            if line.startswith('DISCORD_BOT_TOKEN='):
                return line.split('=', 1)[1].strip()
    raise ValueError("DISCORD_BOT_TOKEN not found in .env")

def send_message(channel_id: str, content: str, attachment: str = None):
    token = load_token()
    headers = {"Authorization": f"Bot {token}"}
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

    if attachment:
        # Send with file attachment
        with open(attachment, 'rb') as f:
            files = {'file': (Path(attachment).name, f)}
            data = {'content': content} if content else {}
            r = requests.post(url, headers=headers, data=data, files=files)
    else:
        # Send text only
        json_data = {"content": content}
        r = requests.post(url, headers=headers, json=json_data)

    if r.status_code in (200, 201):
        print(f"Message sent to channel {channel_id}")
        return True
    else:
        print(f"Error {r.status_code}: {r.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Send Discord message via API')
    parser.add_argument('--channel-id', required=True, help='Discord Channel ID')
    parser.add_argument('--content', default="", help='Message content')
    parser.add_argument('-a', '--attach', help='File to attach')
    args = parser.parse_args()

    send_message(args.channel_id, args.content, args.attach)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Fetch Discord messages directly from API (more reliable than bot inbox)"""
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

def fetch_messages(channel_id: str, limit: int = 10):
    token = load_token()
    headers = {"Authorization": f"Bot {token}"}
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
        return []
    return r.json()

def main():
    parser = argparse.ArgumentParser(description='Fetch Discord messages from API')
    parser.add_argument('-n', type=int, default=10, help='Number of messages (max 100)')
    parser.add_argument('-c', '--channel', default=DEFAULT_CHANNEL, help='Channel ID')
    parser.add_argument('--json', action='store_true', help='Output raw JSON messages')
    args = parser.parse_args()

    messages = fetch_messages(args.channel, min(args.n, 100))

    if args.json:
        import json
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        return

    if not messages:
        print("No messages or error fetching.")
        return

    print(f"=== Discord Messages ({len(messages)} messages) ===\n")
    for msg in reversed(messages):
        ts = msg['timestamp'][:19]
        username = msg['author']['username']
        displayname = msg['author'].get('global_name') or username
        author_id = msg['author']['id']
        content = msg['content']
        print(f'[{ts}] {author_id}/{username}/{displayname} -> "{content}"')
        if msg.get('attachments'):
            for att in msg['attachments']:
                print(f"  [ATTACHMENT] {att.get('filename')}: {att.get('url')}")
        if msg.get('embeds'):
            for emb in msg['embeds']:
                if emb.get('description'):
                    print(f"  [EMBED] {emb.get('description')[:200]}...")
        print()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Read messages from Discord inbox"""
import json
import os
import argparse

INBOX_FILE = "discord_inbox.json"

def main():
    parser = argparse.ArgumentParser(description='Read Discord messages')
    parser.add_argument('-n', type=int, default=10, help='Number of messages to show')
    parser.add_argument('--clear', action='store_true', help='Clear inbox after reading')
    parser.add_argument('--channel', help='Filter by channel name')
    args = parser.parse_args()

    if not os.path.exists(INBOX_FILE):
        print("No messages yet.")
        return

    with open(INBOX_FILE, 'r') as f:
        messages = json.load(f)

    if args.channel:
        messages = [m for m in messages if args.channel.lower() in m.get('channel', '').lower()]

    messages = messages[-args.n:]

    if not messages:
        print("No messages.")
        return

    print(f"=== Discord Inbox ({len(messages)} messages) ===\n")
    for msg in messages:
        ts = msg.get('timestamp', '')[:19]
        server = msg.get('server', 'DM')
        channel = msg.get('channel', 'DM')
        author = msg.get('author', 'unknown')
        content = msg.get('content', '')
        channel_id = msg.get('channel_id', '')

        print(f"[{ts}] {server}#{channel} (id:{channel_id})")
        print(f"  {author}: {content}")
        print()

    if args.clear:
        with open(INBOX_FILE, 'w') as f:
            json.dump([], f)
        print("Inbox cleared.")

if __name__ == '__main__':
    main()

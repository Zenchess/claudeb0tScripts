#!/usr/bin/env python3
"""Send a message to Discord"""
import json
import os
import argparse

OUTBOX_FILE = "discord_outbox.json"

def main():
    parser = argparse.ArgumentParser(description='Send Discord message')
    parser.add_argument('channel_id', help='Channel ID to send to')
    parser.add_argument('message', help='Message to send')
    args = parser.parse_args()

    outbox = []
    if os.path.exists(OUTBOX_FILE):
        with open(OUTBOX_FILE, 'r') as f:
            outbox = json.load(f)

    outbox.append({
        'channel_id': args.channel_id,
        'content': args.message
    })

    with open(OUTBOX_FILE, 'w') as f:
        json.dump(outbox, f, indent=2)

    print(f"Message queued for channel {args.channel_id}")
    print("(Bot will send it within 2 seconds)")

if __name__ == '__main__':
    main()

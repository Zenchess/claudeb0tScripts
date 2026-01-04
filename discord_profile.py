#!/usr/bin/env python3
"""Request Discord profile lookup via bot"""
import json
import argparse
import os

OUTBOX_FILE = "discord_outbox.json"
INBOX_FILE = "discord_inbox.json"

# Default guild ID (Claudeb0t server)
DEFAULT_GUILD = 1456288519403208703

def load_outbox():
    if os.path.exists(OUTBOX_FILE):
        with open(OUTBOX_FILE, 'r') as f:
            return json.load(f)
    return []

def save_outbox(messages):
    with open(OUTBOX_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def request_profile(username=None, user_id=None, guild_id=DEFAULT_GUILD):
    outbox = load_outbox()
    request = {
        "type": "profile",
        "guild_id": str(guild_id)
    }
    if user_id:
        request["user_id"] = str(user_id)
    elif username:
        request["username"] = username
    else:
        print("Error: Provide --username or --user-id")
        return

    outbox.append(request)
    save_outbox(outbox)
    print(f"Profile request queued for: {username or user_id}")
    print("Bot will fetch profile and add to inbox within 2 seconds")
    print("Check with: python3 discord_read.py -n 5")

def main():
    parser = argparse.ArgumentParser(description='Request Discord profile lookup')
    parser.add_argument('--username', '-u', help='Username or display name to look up')
    parser.add_argument('--user-id', '-i', help='User ID to look up')
    parser.add_argument('--guild', '-g', default=DEFAULT_GUILD, help='Guild ID')
    args = parser.parse_args()

    request_profile(args.username, args.user_id, args.guild)

if __name__ == '__main__':
    main()

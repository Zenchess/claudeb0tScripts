#!/usr/bin/env python3
"""
Unified monitor for Discord + Hackmud Chat API
Polls both sources and forwards in-game tells to Discord
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

# File paths
DIR = os.path.dirname(os.path.abspath(__file__))
DISCORD_INBOX = os.path.join(DIR, "discord_inbox.json")
DISCORD_OUTBOX = os.path.join(DIR, "discord_outbox.json")
CHAT_TOKEN_FILE = os.path.join(DIR, "chat_token.json")
LAST_POLL_FILE = os.path.join(DIR, "last_poll.json")
TRANSACTIONS_LOG = os.path.join(DIR, "transactions.log")

# Discord channel IDs
DISCORD_GENERAL = "1456288519403208800"

# Hackmud Chat API
API_BASE = "https://www.hackmud.com/mobile"

def api_post(endpoint, data):
    """Make a POST request to the hackmud API"""
    url = f"{API_BASE}/{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_chat_token():
    """Load hackmud chat token"""
    if os.path.exists(CHAT_TOKEN_FILE):
        with open(CHAT_TOKEN_FILE, 'r') as f:
            return json.load(f).get('chat_token')
    return None

def get_last_poll_time():
    """Get last poll timestamp"""
    if os.path.exists(LAST_POLL_FILE):
        with open(LAST_POLL_FILE, 'r') as f:
            return json.load(f).get('last_poll', time.time() - 60)
    return time.time() - 60

def save_last_poll_time(t):
    """Save last poll timestamp"""
    with open(LAST_POLL_FILE, 'w') as f:
        json.dump({'last_poll': t}, f)

def poll_hackmud_chat(token, usernames=['claudeb0t', 'claud3']):
    """Poll hackmud chat API for new messages"""
    after = get_last_poll_time()
    data = api_post("chats.json", {
        "chat_token": token,
        "usernames": usernames,
        "after": after
    })

    if data.get('ok'):
        save_last_poll_time(time.time())
        return data.get('chats', {})
    return {}

def send_to_discord(channel_id, message):
    """Queue a message to be sent to Discord"""
    outbox = []
    if os.path.exists(DISCORD_OUTBOX):
        try:
            with open(DISCORD_OUTBOX, 'r') as f:
                outbox = json.load(f)
        except:
            outbox = []

    outbox.append({
        'channel_id': channel_id,
        'content': message
    })

    with open(DISCORD_OUTBOX, 'w') as f:
        json.dump(outbox, f, indent=2)

def format_tell_for_discord(msg):
    """Format an in-game tell for Discord"""
    ts = datetime.fromtimestamp(msg['t']).strftime('%H:%M:%S')
    from_user = msg.get('from_user', '???')
    content = msg.get('msg', '')
    return f"**In-game tell:**\n`[{ts}] from {from_user}: {content}`"

def main():
    print("Starting unified monitor (Discord + Hackmud Chat API)...")

    # Load chat token
    token = load_chat_token()
    if not token:
        print("ERROR: No chat token found. Run chat_api.py --setup first.")
        sys.exit(1)

    print(f"Chat token loaded. Monitoring...")
    interval = 5  # Poll every 5 seconds

    seen_tells = set()  # Track tells we've already forwarded

    try:
        while True:
            # Poll hackmud chat API
            chats = poll_hackmud_chat(token)

            for user, msgs in chats.items():
                for msg in msgs:
                    # Check if this is a direct tell (no channel = DM)
                    if 'channel' not in msg and not msg.get('is_join') and not msg.get('is_leave'):
                        # This is a tell/DM
                        msg_id = f"{msg['t']}_{msg.get('from_user', '')}"
                        if msg_id not in seen_tells:
                            seen_tells.add(msg_id)
                            discord_msg = format_tell_for_discord(msg)
                            send_to_discord(DISCORD_GENERAL, discord_msg)
                            print(f"[TELL] {msg.get('from_user', '???')}: {msg.get('msg', '')}")

                    # Also check for GC transactions in messages
                    content = msg.get('msg', '')
                    if 'GC' in content and ('received' in content.lower() or 'sent' in content.lower()):
                        print(f"[GC?] {content}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitor stopped.")

if __name__ == '__main__':
    main()

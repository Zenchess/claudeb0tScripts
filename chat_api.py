#!/usr/bin/env python3
"""
Hackmud Chat API client
Usage:
  python3 chat_api.py --setup              # Get initial token (run chat_pass in game first)
  python3 chat_api.py --poll               # Poll for new messages
  python3 chat_api.py --send <user> <channel> <msg>  # Send channel message
  python3 chat_api.py --tell <user> <target> <msg>   # Send DM
  python3 chat_api.py --watch              # Continuously watch for messages
"""

import urllib.request
import urllib.error
import json
import time
import sys
import os
from datetime import datetime

API_BASE = "https://www.hackmud.com/mobile"

def api_post(endpoint, data):
    """Make a POST request to the API"""
    url = f"{API_BASE}/{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": str(e)}
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "chat_token.json")
LAST_POLL_FILE = os.path.join(os.path.dirname(__file__), "last_poll.json")

def load_token():
    """Load chat token from file"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get('chat_token')
    return None

def save_token(token):
    """Save chat token to file"""
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'chat_token': token, 'saved_at': time.time()}, f)

def get_token(password):
    """Exchange chat_pass password for a token"""
    data = api_post("get_token.json", {"pass": password})
    if data.get('ok'):
        save_token(data['chat_token'])
        return data['chat_token']
    else:
        print(f"Error getting token: {data}")
        return None

def get_account_data(token):
    """Get all users and their channels"""
    return api_post("account_data.json", {"chat_token": token})

def get_last_poll_time():
    """Get the timestamp of last poll"""
    if os.path.exists(LAST_POLL_FILE):
        with open(LAST_POLL_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_poll', time.time() - 60)
    return time.time() - 60  # Default to 1 minute ago

def save_last_poll_time(t):
    """Save the timestamp of last poll"""
    with open(LAST_POLL_FILE, 'w') as f:
        json.dump({'last_poll': t}, f)

def poll_messages(token, usernames=None):
    """Poll for new messages since last check"""
    if usernames is None:
        # Get all usernames from account data
        account = get_account_data(token)
        if 'users' in account:
            usernames = list(account['users'].keys())
        else:
            usernames = ['claudeb0t', 'claud3']

    after = get_last_poll_time()

    data = api_post("chats.json", {
        "chat_token": token,
        "usernames": usernames,
        "after": after
    })

    if data.get('ok'):
        save_last_poll_time(time.time())
        return data.get('chats', {})
    else:
        print(f"Error polling: {data}")
        return {}

def send_channel_message(token, username, channel, msg):
    """Send a message to a channel"""
    return api_post("create_chat.json", {
        "chat_token": token,
        "username": username,
        "channel": channel,
        "msg": msg
    })

def send_tell(token, username, target, msg):
    """Send a direct message"""
    return api_post("create_chat.json", {
        "chat_token": token,
        "username": username,
        "tell": target,
        "msg": msg
    })

def format_message(msg):
    """Format a message for display"""
    ts = datetime.fromtimestamp(msg['t']).strftime('%H:%M:%S')
    from_user = msg.get('from_user', '???')
    content = msg.get('msg', '')

    if msg.get('is_join'):
        return f"[{ts}] {from_user} joined {msg.get('channel', '???')}"
    elif msg.get('is_leave'):
        return f"[{ts}] {from_user} left {msg.get('channel', '???')}"
    elif 'channel' in msg:
        return f"[{ts}] #{msg['channel']} <{from_user}> {content}"
    else:
        return f"[{ts}] DM from {from_user}: {content}"

def watch_messages(token, interval=3):
    """Continuously watch for new messages"""
    print("Watching for messages (Ctrl+C to stop)...", flush=True)

    # Get usernames
    account = get_account_data(token)
    usernames = list(account.get('users', {}).keys()) or ['claudeb0t', 'claud3']
    print(f"Monitoring users: {', '.join(usernames)}", flush=True)

    try:
        while True:
            chats = poll_messages(token, usernames)

            # Collect all messages
            all_msgs = []
            for user, msgs in chats.items():
                for msg in msgs:
                    msg['_for_user'] = user
                    all_msgs.append(msg)

            # Sort by timestamp
            all_msgs.sort(key=lambda x: x['t'])

            # Print new messages
            for msg in all_msgs:
                print(format_message(msg), flush=True)

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching.", flush=True)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == '--setup':
        if len(sys.argv) < 3:
            print("Usage: python3 chat_api.py --setup <password from chat_pass>")
            return
        password = sys.argv[2]
        token = get_token(password)
        if token:
            print(f"Token saved! Valid for 45 days.")
            account = get_account_data(token)
            if 'users' in account:
                print(f"Users: {', '.join(account['users'].keys())}")

    elif cmd == '--poll':
        token = load_token()
        if not token:
            print("No token found. Run --setup first.")
            return
        chats = poll_messages(token)
        for user, msgs in chats.items():
            for msg in msgs:
                print(format_message(msg))

    elif cmd == '--watch':
        token = load_token()
        if not token:
            print("No token found. Run --setup first.")
            return
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        watch_messages(token, interval)

    elif cmd == '--send':
        if len(sys.argv) < 5:
            print("Usage: python3 chat_api.py --send <username> <channel> <message>")
            return
        token = load_token()
        if not token:
            print("No token found. Run --setup first.")
            return
        result = send_channel_message(token, sys.argv[2], sys.argv[3], ' '.join(sys.argv[4:]))
        print(result)

    elif cmd == '--tell':
        if len(sys.argv) < 5:
            print("Usage: python3 chat_api.py --tell <username> <target> <message>")
            return
        token = load_token()
        if not token:
            print("No token found. Run --setup first.")
            return
        result = send_tell(token, sys.argv[2], sys.argv[3], ' '.join(sys.argv[4:]))
        print(result)

    elif cmd == '--account':
        token = load_token()
        if not token:
            print("No token found. Run --setup first.")
            return
        account = get_account_data(token)
        print(json.dumps(account, indent=2))

    else:
        print(__doc__)

if __name__ == '__main__':
    main()

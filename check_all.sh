#!/bin/bash
# Combined check script for game chat and Discord

echo "=== GAME CHAT (last 15) ==="
tail -15 /tmp/chat_watch.log 2>/dev/null || echo "Chat watcher not running"

echo ""
echo "=== DISCORD (last 8) ==="
python3 discord_read.py -n 8

echo ""
echo "=== INBOX SUMMARY ==="
python3 check_inbox.py 3 2>/dev/null | tail -5

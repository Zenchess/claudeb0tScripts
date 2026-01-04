#!/bin/bash
# Notification hook - logs notifications

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"

input=$(cat)
notification_type=$(echo "$input" | jq -r '.type // "unknown"')

echo "[$(date)] Notification hook: type=$notification_type" >> "$LOG"

exit 0

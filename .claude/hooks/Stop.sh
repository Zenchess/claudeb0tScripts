#!/bin/bash
# Stop hook - makes Claude continue playing hackmud persistently
# NEVER let Claude stop unless user explicitly intervenes

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"
COUNTER_FILE="/home/jacob/hackmud/.claude/hooks/stop_counter"

input=$(cat)
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')

# Get current counter
if [ -f "$COUNTER_FILE" ]; then
  counter=$(cat "$COUNTER_FILE")
else
  counter=0
fi

echo "[$(date)] Stop hook fired. stop_hook_active=$stop_hook_active counter=$counter" >> "$LOG"

# Only allow stop after 50+ blocks (very high safety limit)
# Ignore stop_hook_active - always block unless counter is very high
if [ "$counter" -ge 50 ]; then
  echo "[$(date)] Allowing stop after 50 blocks (safety limit reached)" >> "$LOG"
  echo "0" > "$COUNTER_FILE"
  exit 0
fi

# Increment counter and block stop
counter=$((counter + 1))
echo "$counter" > "$COUNTER_FILE"

echo "[$(date)] Blocking stop #$counter - telling Claude to continue" >> "$LOG"
cat << 'EOF'
{"decision": "block", "reason": "Keep doing whatever you want in Hackmud - making scripts, PvP, hacking NPCs, chatting with players, exploring sectors, etc. Check Discord and n00bz chat regularly. Have fun!"}
EOF
exit 0

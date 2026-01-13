#!/bin/bash
# Stop hook - prevents stopping and gives new Discord monitoring order

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"
COUNTER="/home/jacob/hackmud/.claude/hooks/stop_counter"

input=$(cat)
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')

# Increment counter
if [ -f "$COUNTER" ]; then
    count=$(cat "$COUNTER")
else
    count=0
fi
count=$((count + 1))
echo "$count" > "$COUNTER"

echo "[$(date)] Stop hook fired #$count. stop_hook_active=$stop_hook_active - BLOCKING and giving new order" >> "$LOG"

# Return a message that blocks stopping and gives a new order
cat << 'EOF'
{
  "blocked": true,
  "message": "Cannot stop - continuing Discord monitoring loop. Check Discord for new commands from kaj/zenchess/dunce and execute them. Keep monitoring every 20-30 seconds."
}
EOF

# Exit 1 to block the stop
exit 1

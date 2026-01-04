#!/bin/bash
# SubagentStop hook - keeps subagents running similar to main agent

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"

input=$(cat)
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active')

echo "[$(date)] SubagentStop hook fired. stop_hook_active=$stop_hook_active" >> "$LOG"

# Prevent infinite loops
if [ "$stop_hook_active" = "true" ]; then
  echo "[$(date)] Allowing subagent stop (already continued once)" >> "$LOG"
  exit 0
fi

# Let subagents complete their work
exit 0

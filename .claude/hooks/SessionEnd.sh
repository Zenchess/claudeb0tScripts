#!/bin/bash
# SessionEnd hook - logs session end and saves state

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"

echo "[$(date)] Session ending - saving state" >> "$LOG"

# Log final balance check
echo "[$(date)] Session ended" >> "$LOG"

exit 0

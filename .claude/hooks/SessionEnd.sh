#!/bin/bash
# SessionEnd hook - logs session end and saves state

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"

echo "[$(date)] Session ending - saving state" >> "$LOG"

# Reminder: Check Discord and update memory before session ends
echo "[$(date)] REMINDER: Check Discord for pending tasks before ending" >> "$LOG"
echo "[$(date)] REMINDER: Update claude_memory.txt with session summary" >> "$LOG"

# Log final balance check
echo "[$(date)] Session ended" >> "$LOG"

exit 0

#!/bin/bash
# Session start hook - logs session start and injects context

# Log session start
echo "[$(date)] Session started" >> /home/jacob/hackmud/.claude/hooks/hook_debug.log

# Output context for Claude at session start
cat << 'EOF'
{"additionalContext": "You are claudeb0t playing hackmud autonomously. Read claude_memory.txt and discord_inbox.json to catch up, then continue playing!"}
EOF
exit 0

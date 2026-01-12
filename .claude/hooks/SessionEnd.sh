#!/bin/bash
# SessionEnd hook - prevents session from ending and continues monitoring

LOG="/home/jacob/hackmud/.claude/hooks/hook_debug.log"

echo "[$(date)] SessionEnd hook fired - BLOCKING and ordering continued monitoring" >> "$LOG"

# Block session end and give order to continue
cat << 'EOF'
{
  "blocked": true,
  "message": "Session cannot end - continue monitoring Discord for commands from kaj/zenchess/dunce. Check every 20-30 seconds and execute any tasks they request."
}
EOF

# Exit 1 to block
exit 1

#!/bin/bash
# Wrapper to run Claude Code autonomously on hackmud
# Restarts Claude if it exits

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PROMPT="You are playing hackmud autonomously. Your goal:
1. Make sure mem_scanner.py is running in watch mode
2. Use send_command.py to interact with the game
3. Use get_responses.py to read game output
4. Crack NPCs, collect GC, transfer to zenchess
5. Keep playing - find new targets, crack them, repeat

Start by checking if the scanner is running, then check game status."

while true; do
    echo "=== Starting Claude Code session at $(date) ==="

    # Run Claude Code with the prompt, auto-accept tool calls
    claude --dangerously-skip-permissions -p "$PROMPT"

    EXIT_CODE=$?
    echo "=== Claude exited with code $EXIT_CODE at $(date) ==="

    # Brief pause before restart
    sleep 5
done

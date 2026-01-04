#!/bin/bash
# Start the hackmud memory scanner as a background daemon

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/responses.log"
PID_FILE="$SCRIPT_DIR/scanner.pid"

# Kill existing scanner if running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping existing scanner (PID $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# Start the scanner
echo "Starting memory scanner..."
echo "Log file: $LOG_FILE"

nohup python3 "$SCRIPT_DIR/mem_scanner.py" --watch > /dev/null 2>&1 &
echo $! > "$PID_FILE"

echo "Scanner started with PID $(cat "$PID_FILE")"
echo "Responses will be written to: $LOG_FILE"

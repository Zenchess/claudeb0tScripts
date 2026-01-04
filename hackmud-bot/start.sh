#!/bin/bash
# Start the hackmud bot system
# This starts:
# 1. The memory scanner (if not already running)
# 2. The Node.js web server
# 3. The Python bot agent

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LINUX_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "   HACKMUD AUTONOMOUS BOT SYSTEM"
echo "========================================="
echo ""

# Check for required tools
command -v node >/dev/null 2>&1 || { echo "Error: Node.js is required. Install with: sudo pacman -S nodejs npm"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: Python 3 is required."; exit 1; }
command -v claude >/dev/null 2>&1 || { echo "Error: Claude Code CLI is required."; exit 1; }

# Install npm dependencies if needed
if [ ! -d "$SCRIPT_DIR/server/node_modules" ]; then
    echo "[1/4] Installing Node.js dependencies..."
    cd "$SCRIPT_DIR/server"
    npm install
    cd "$SCRIPT_DIR"
else
    echo "[1/4] Node.js dependencies OK"
fi

# Check/create virtual environment
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "[2/4] Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    "$SCRIPT_DIR/venv/bin/pip" install 'python-socketio[client]'
else
    echo "[2/4] Python venv OK"
fi

PYTHON="$SCRIPT_DIR/venv/bin/python"

# Start memory scanner if not running
if [ -f "$LINUX_DIR/scanner.pid" ]; then
    OLD_PID=$(cat "$LINUX_DIR/scanner.pid")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[3/4] Memory scanner already running (PID $OLD_PID)"
    else
        echo "[3/4] Starting memory scanner..."
        bash "$LINUX_DIR/start_scanner.sh"
    fi
else
    echo "[3/4] Starting memory scanner..."
    bash "$LINUX_DIR/start_scanner.sh"
fi

# Initialize memory and state files if they don't exist
if [ ! -f "$SCRIPT_DIR/bot/memory.json" ]; then
    echo '{"known_npcs":[],"cracked_npcs":[],"failed_npcs":[],"lock_solutions":{},"gc_transferred":0,"notes":[],"strategies":[]}' > "$SCRIPT_DIR/bot/memory.json"
fi

if [ ! -f "$SCRIPT_DIR/bot/state.json" ]; then
    echo '{"status":"idle","current_task":null,"last_command":null,"user_message_queue":[]}' > "$SCRIPT_DIR/bot/state.json"
fi

echo "[4/4] Starting servers..."
echo ""
echo "========================================="
echo "  Web Interface: http://localhost:3000"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $NODE_PID 2>/dev/null
    kill $BOT_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Node.js server
cd "$SCRIPT_DIR/server"
node index.js &
NODE_PID=$!
echo "Node.js server started (PID $NODE_PID)"

# Wait for server to start
sleep 2

# Start Python bot agent
cd "$SCRIPT_DIR"
$PYTHON bot/agent.py "$@" &
BOT_PID=$!
echo "Bot agent started (PID $BOT_PID)"

# Wait for both processes
wait

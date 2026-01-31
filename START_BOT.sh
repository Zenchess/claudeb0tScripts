#!/bin/bash
# Quick start script for autonomous bot

cd /home/jacob/hackmud

echo "🤖 Starting Autonomous OpenRouter Bot..."
echo "   Model: minimax/minimax-m2"
echo "   Base: /home/jacob/hackmud"
echo ""
echo "Starting bot in background..."

# Start bot with nohup
nohup python3 autonomous_agent.py >> /tmp/autonomous_agent.log 2>&1 &

# Save PID
echo $! > autonomous_agent.pid

# Wait for startup
sleep 2

# Check if running
if ps -p $(cat autonomous_agent.pid) > /dev/null; then
    echo "✅ Bot started successfully (PID: $(cat autonomous_agent.pid))"
    echo ""
    echo "Monitoring logs (Ctrl+C to exit monitor)..."
    echo "================================================"
    tail -f /tmp/autonomous_agent.log
else
    echo "❌ Failed to start bot"
    echo "Check /tmp/autonomous_agent.log for errors"
    exit 1
fi

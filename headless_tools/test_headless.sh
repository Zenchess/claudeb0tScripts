#!/bin/bash
# Test script for headless hackmud with GL nullification
#
# Usage: ./test_headless.sh [--no-nullify] [--debug]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HACKMUD_PATH="$HOME/.local/share/Steam/steamapps/common/hackmud/hackmud.x86_64"
GL_NULLIFY="$SCRIPT_DIR/gl_nullify.so"
DISPLAY_NUM=99

# Parse args
USE_NULLIFY=1
DEBUG=0
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-nullify) USE_NULLIFY=0; shift ;;
        --debug) DEBUG=1; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=== Headless Hackmud Test ==="
echo "GL Nullify: $([ $USE_NULLIFY -eq 1 ] && echo 'ENABLED' || echo 'DISABLED')"
echo "Debug: $([ $DEBUG -eq 1 ] && echo 'ENABLED' || echo 'DISABLED')"
echo ""

# Check if Xvfb is already running on this display
if xdpyinfo -display :$DISPLAY_NUM >/dev/null 2>&1; then
    echo "[INFO] Xvfb already running on :$DISPLAY_NUM"
else
    echo "[INFO] Starting Xvfb on :$DISPLAY_NUM..."
    Xvfb :$DISPLAY_NUM -screen 0 800x600x24 &
    XVFB_PID=$!
    echo "[INFO] Xvfb started with PID $XVFB_PID"
    sleep 2
fi

export DISPLAY=:$DISPLAY_NUM

# Build command
CMD="$HACKMUD_PATH"

if [ $USE_NULLIFY -eq 1 ]; then
    if [ ! -f "$GL_NULLIFY" ]; then
        echo "[ERROR] gl_nullify.so not found at $GL_NULLIFY"
        echo "Compile with: gcc -shared -fPIC -o gl_nullify.so gl_nullify.c -ldl"
        exit 1
    fi
    export LD_PRELOAD="$GL_NULLIFY"
    echo "[INFO] LD_PRELOAD set to $GL_NULLIFY"
fi

echo "[INFO] Starting hackmud..."
echo "[INFO] Command: DISPLAY=$DISPLAY LD_PRELOAD=$LD_PRELOAD $CMD"

# Redirect stderr to see GL nullify logs
if [ $DEBUG -eq 1 ]; then
    $CMD 2>&1 | tee /tmp/hackmud_headless.log &
else
    $CMD 2>/tmp/hackmud_headless_gl.log &
fi

HACKMUD_PID=$!
echo "[INFO] Hackmud started with PID $HACKMUD_PID"
echo ""

# Wait a bit then check
sleep 5

if kill -0 $HACKMUD_PID 2>/dev/null; then
    echo "[SUCCESS] Hackmud is running!"
    echo ""

    # Check CPU usage
    CPU=$(ps -p $HACKMUD_PID -o %cpu= 2>/dev/null || echo "N/A")
    MEM=$(ps -p $HACKMUD_PID -o %mem= 2>/dev/null || echo "N/A")
    echo "[INFO] CPU: ${CPU}%  MEM: ${MEM}%"

    # Show some GL logs if they exist
    if [ -f /tmp/hackmud_headless_gl.log ]; then
        echo ""
        echo "[DEBUG] Last 10 GL calls:"
        tail -10 /tmp/hackmud_headless_gl.log
    fi

    echo ""
    echo "[INFO] To send input: DISPLAY=:$DISPLAY_NUM xdotool type 'your_command'"
    echo "[INFO] To kill: kill $HACKMUD_PID"
else
    echo "[FAILED] Hackmud crashed or failed to start"
    echo ""
    echo "[DEBUG] Last output:"
    tail -20 /tmp/hackmud_headless.log 2>/dev/null || cat /tmp/hackmud_headless_gl.log 2>/dev/null || echo "(no logs)"
    exit 1
fi

#!/bin/bash
# Run kernel.hardline and complete the connection sequence (no focus needed)
# Supports headless mode (Xvfb) by reading display from /tmp/headlessHM_display

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Get display - use headless if available
if [ -f /tmp/headlessHM_display ]; then
    export DISPLAY=":$(cat /tmp/headlessHM_display)"
    echo "Using headless display: $DISPLAY"
fi

# Get hackmud window ID
WINDOW_ID=$(xdotool search --name hackmud | head -1)
if [ -z "$WINDOW_ID" ]; then
    echo "Hackmud window not found!"
    exit 1
fi

echo "Found hackmud window: $WINDOW_ID"

echo "Sending kernel.hardline..."
xdotool type --window "$WINDOW_ID" "kernel.hardline"
sleep 0.1
xdotool key --window "$WINDOW_ID" Return

echo "Waiting 10 seconds for hardline animation..."
sleep 10

echo "Spamming 0-9 keys fast (30 iterations)..."
for i in {1..30}; do
  for key in 1 2 3 4 5 6 7 8 9 0; do
    xdotool key --window "$WINDOW_ID" "$key"
  done
done

echo "Hardline complete!"

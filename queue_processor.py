#!/usr/bin/env python3
"""
Background queue processor for hackmud commands
Processes commands from the FIFO queue one at a time
"""

import subprocess
import time
import signal
import sys
from pathlib import Path
from command_queue import CommandQueue

# Flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) for graceful shutdown"""
    global running
    print("\n🛑 Shutting down queue processor...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def execute_command(command: str) -> bool:
    """
    Execute a hackmud command using send_command.py
    Returns: True if successful, False otherwise
    """
    try:
        result = subprocess.run(
            ['python3', 'send_command.py', command],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠️  Command timed out: {command[:50]}...")
        return False
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False

def main():
    """Main queue processor loop"""
    print("🚀 Command queue processor started")
    print("Processing commands in FIFO order...")
    print("Press Ctrl+C to stop\n")

    queue = CommandQueue()

    while running:
        # Check for commands in queue
        cmd_entry = queue.pop()

        if cmd_entry:
            command = cmd_entry['command']
            username = cmd_entry.get('username', 'unknown')
            print(f"⚙️  Executing: {command[:60]}{'...' if len(command) > 60 else ''} (from {username})")

            # Execute command
            success = execute_command(command)

            if success:
                print(f"✅ Command completed")
            else:
                print(f"❌ Command failed")

            # Mark as complete and remove from queue
            queue.complete(command)

            # Small delay between commands
            time.sleep(0.1)
        else:
            # No commands, wait a bit
            time.sleep(0.05)

    print("Queue processor stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Queue processor interrupted")
        sys.exit(0)

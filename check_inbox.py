#!/usr/bin/env python3
"""
Check inbox for important messages (DMs and mentions)
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
INBOX_FILE = SCRIPT_DIR / "inbox.log"

def main():
    if not INBOX_FILE.exists():
        print("No inbox file yet - no important messages received.")
        return

    # Read and display inbox
    content = INBOX_FILE.read_text()

    if not content.strip():
        print("Inbox is empty.")
        return

    lines = content.strip().split('\n')

    # Show last N messages (default 10)
    n = 10
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass

    # Filter out empty lines and show recent messages
    messages = [l for l in lines if l.strip()]
    recent = messages[-n:] if len(messages) > n else messages

    print(f"=== INBOX ({len(messages)} total messages, showing last {len(recent)}) ===\n")
    for msg in recent:
        print(msg)
    print()

    if '--clear' in sys.argv:
        INBOX_FILE.write_text('')
        print("Inbox cleared.")

if __name__ == '__main__':
    main()

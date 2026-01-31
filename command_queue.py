#!/usr/bin/env python3
"""
FIFO command queue system for hackmud web interface
Thread-safe command queueing and processing
"""

import fcntl
import json
import time
from pathlib import Path
from typing import List, Optional

QUEUE_FILE = Path(__file__).parent / "command_queue.json"

class CommandQueue:
    """Thread-safe FIFO command queue using file locking"""

    def __init__(self, queue_file: Path = QUEUE_FILE):
        self.queue_file = queue_file
        # Ensure queue file exists
        if not self.queue_file.exists():
            self._write_queue([])

    def _read_queue(self) -> List[dict]:
        """Read queue with file locking"""
        with open(self.queue_file, 'r+') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _write_queue(self, queue: List[dict]):
        """Write queue with file locking"""
        with open(self.queue_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(queue, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def push(self, command: str, user_id: Optional[int] = None, username: Optional[str] = None) -> int:
        """
        Add command to queue (FIFO)
        Returns: position in queue (0-indexed)
        """
        queue = self._read_queue()

        entry = {
            'command': command,
            'user_id': user_id,
            'username': username,
            'timestamp': time.time(),
            'status': 'pending'
        }

        queue.append(entry)
        self._write_queue(queue)

        return len(queue) - 1

    def pop(self) -> Optional[dict]:
        """
        Remove and return first command from queue
        Returns: command entry or None if queue is empty
        """
        queue = self._read_queue()

        if not queue:
            return None

        # Get first pending command
        for i, entry in enumerate(queue):
            if entry['status'] == 'pending':
                # Mark as processing
                entry['status'] = 'processing'
                self._write_queue(queue)
                return entry

        return None

    def complete(self, command: str):
        """Mark command as completed and remove from queue"""
        queue = self._read_queue()

        # Remove completed command
        queue = [e for e in queue if not (e['command'] == command and e['status'] == 'processing')]

        self._write_queue(queue)

    def size(self) -> int:
        """Get number of pending commands in queue"""
        queue = self._read_queue()
        return sum(1 for e in queue if e['status'] == 'pending')

    def clear(self):
        """Clear all commands from queue"""
        self._write_queue([])

if __name__ == "__main__":
    # Test the queue
    q = CommandQueue()
    print(f"Queue size: {q.size()}")

    # Test push
    pos = q.push("test command", user_id=123, username="testuser")
    print(f"Pushed command at position {pos}")
    print(f"Queue size: {q.size()}")

    # Test pop
    cmd = q.pop()
    print(f"Popped command: {cmd}")

    # Test complete
    if cmd:
        q.complete(cmd['command'])
        print(f"Completed command. Queue size: {q.size()}")

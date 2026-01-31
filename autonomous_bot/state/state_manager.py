"""Manages persistent bot state with atomic writes and logging"""

import json
import time
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime

from .schemas import BotState, Action, ActionResult


class StateManager:
    """Manages persistent bot state with safety"""

    def __init__(self, state_dir: Optional[Path] = None):
        if state_dir is None:
            state_dir = Path(__file__).parent.parent / "state"

        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.state_dir / "bot_state.json"
        self.action_log = self.state_dir / "action_history.jsonl"
        self.conversation_log = self.state_dir / "conversation_history.jsonl"

        self._lock = threading.RLock()
        self._current_state: Optional[BotState] = None

    def load_state(self) -> BotState:
        """Load persistent state with validation"""
        with self._lock:
            if self.state_file.exists():
                try:
                    with open(self.state_file, 'r') as f:
                        data = json.load(f)
                        self._current_state = BotState.from_dict(data)
                        return self._current_state
                except Exception as e:
                    print(f"Error loading state: {e}, using defaults")

            # Use default state
            self._current_state = BotState.default()
            return self._current_state

    def save_state(self, state: BotState) -> bool:
        """Save state atomically (write to .tmp first, then replace)"""
        with self._lock:
            try:
                # Update timestamp
                state.last_updated = datetime.now().timestamp()

                # Write to temporary file
                tmp_file = self.state_file.with_suffix('.tmp')
                with open(tmp_file, 'w') as f:
                    json.dump(state.to_dict(), f, indent=2)

                # Atomic replace
                tmp_file.replace(self.state_file)

                self._current_state = state
                return True
            except Exception as e:
                print(f"Error saving state: {e}")
                return False

    def log_action(self, action: Action, result: ActionResult) -> bool:
        """Log action to append-only history (JSONL format)"""
        with self._lock:
            try:
                entry = {
                    'timestamp': datetime.now().isoformat(),
                    'action': action.to_dict(),
                    'result': result.to_dict()
                }
                with open(self.action_log, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
                return True
            except Exception as e:
                print(f"Error logging action: {e}")
                return False

    def log_conversation(self, role: str, content: str) -> bool:
        """Log conversation turn for context reconstruction"""
        with self._lock:
            try:
                entry = {
                    'timestamp': datetime.now().isoformat(),
                    'role': role,  # 'user', 'assistant', 'system'
                    'content': content
                }
                with open(self.conversation_log, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
                return True
            except Exception as e:
                print(f"Error logging conversation: {e}")
                return False

    def get_recent_actions(self, n: int = 10) -> list:
        """Get last N actions from history"""
        with self._lock:
            try:
                if not self.action_log.exists():
                    return []

                actions = []
                with open(self.action_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                actions.append(entry)
                            except json.JSONDecodeError:
                                continue

                return actions[-n:] if actions else []
            except Exception as e:
                print(f"Error reading recent actions: {e}")
                return []

    def get_conversation_context(self, max_turns: int = 20) -> list:
        """Get recent conversation turns for context"""
        with self._lock:
            try:
                if not self.conversation_log.exists():
                    return []

                turns = []
                with open(self.conversation_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                turns.append(entry)
                            except json.JSONDecodeError:
                                continue

                return turns[-max_turns:] if turns else []
            except Exception as e:
                print(f"Error reading conversation context: {e}")
                return []

    def clear_old_logs(self, days: int = 7) -> bool:
        """Clear logs older than N days"""
        with self._lock:
            try:
                cutoff_time = time.time() - (days * 24 * 60 * 60)

                # Rewrite action log, keeping only recent entries
                if self.action_log.exists():
                    new_entries = []
                    with open(self.action_log, 'r') as f:
                        for line in f:
                            if line.strip():
                                try:
                                    entry = json.loads(line)
                                    if entry.get('action', {}).get('created_at', 0) > cutoff_time:
                                        new_entries.append(line.rstrip('\n'))
                                except json.JSONDecodeError:
                                    continue

                    with open(self.action_log, 'w') as f:
                        for entry in new_entries:
                            f.write(entry + '\n')

                # Same for conversation log
                if self.conversation_log.exists():
                    new_entries = []
                    with open(self.conversation_log, 'r') as f:
                        for line in f:
                            if line.strip():
                                try:
                                    entry = json.loads(line)
                                    # Parse ISO timestamp
                                    ts = datetime.fromisoformat(entry.get('timestamp', '')).timestamp()
                                    if ts > cutoff_time:
                                        new_entries.append(line.rstrip('\n'))
                                except (json.JSONDecodeError, ValueError):
                                    continue

                    with open(self.conversation_log, 'w') as f:
                        for entry in new_entries:
                            f.write(entry + '\n')

                return True
            except Exception as e:
                print(f"Error clearing old logs: {e}")
                return False

    def get_state_summary(self) -> dict:
        """Get summary of current state for status reporting"""
        with self._lock:
            if not self._current_state:
                self.load_state()

            state = self._current_state
            return {
                'running': state.running,
                'emergency_stop': state.emergency_stop,
                'balance': state.current_balance,
                'location': state.current_location,
                'active_tasks': len(state.active_tasks),
                'failed_actions': state.failed_actions,
                'uptime_hours': state.uptime_seconds / 3600,
                'total_commands': state.total_commands_sent,
                'total_errors': state.total_errors
            }

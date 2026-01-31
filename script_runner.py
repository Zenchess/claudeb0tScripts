#!/usr/bin/env python3
"""
Sandboxed JavaScript script runner for hackmud bot automation
Uses QuickJS for safe execution with exposed bot API
"""

import quickjs
import threading
import time
import queue
import os
import sys
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

@dataclass
class ScriptState:
    """Current state of the script runner"""
    running: bool = False
    script_code: str = ""
    logs: list = field(default_factory=list)
    error: Optional[str] = None
    started_at: Optional[float] = None

class BotAPI:
    """API exposed to scripts for bot automation"""

    def __init__(self, script_runner: 'ScriptRunner'):
        self.runner = script_runner
        self._stop_requested = False

    def send_command(self, command: str) -> bool:
        """Send a command to hackmud"""
        if self._stop_requested:
            raise InterruptedError("Script stopped")

        self.runner._log(f"[CMD] {command}")

        try:
            from send_command import send_command
            result = send_command(command, press_enter=True)
            return result
        except Exception as e:
            self.runner._log(f"[ERROR] Failed to send command: {e}")
            return False

    def read_terminal(self, lines: int = 50) -> str:
        """Read current terminal content"""
        if self._stop_requested:
            raise InterruptedError("Script stopped")

        try:
            from hackmud.memory import Scanner
            scanner = Scanner()
            scanner.connect()
            text = scanner.read_window('shell', lines=lines)
            scanner.close()
            return '\n'.join(text) if isinstance(text, list) else str(text)
        except Exception as e:
            self.runner._log(f"[ERROR] Failed to read terminal: {e}")
            return ""

    def read_chat(self, lines: int = 30) -> str:
        """Read current chat content"""
        if self._stop_requested:
            raise InterruptedError("Script stopped")

        try:
            from hackmud.memory import Scanner
            scanner = Scanner()
            scanner.connect()
            text = scanner.read_window('chat', lines=lines)
            scanner.close()
            return '\n'.join(text) if isinstance(text, list) else str(text)
        except Exception as e:
            self.runner._log(f"[ERROR] Failed to read chat: {e}")
            return ""

    def sleep(self, ms: int):
        """Sleep for specified milliseconds"""
        if self._stop_requested:
            raise InterruptedError("Script stopped")

        # Sleep in small chunks to allow interruption
        end_time = time.time() + (ms / 1000.0)
        while time.time() < end_time:
            if self._stop_requested:
                raise InterruptedError("Script stopped")
            time.sleep(min(0.1, end_time - time.time()))

    def log(self, message: str):
        """Log a message to script output"""
        self.runner._log(f"[LOG] {message}")

    def get_balance(self) -> str:
        """Read GC balance from badge window"""
        if self._stop_requested:
            raise InterruptedError("Script stopped")

        try:
            from hackmud.memory import Scanner
            scanner = Scanner()
            scanner.connect()
            text = scanner.read_window('badge', lines=10)
            scanner.close()
            return '\n'.join(text) if isinstance(text, list) else str(text)
        except Exception as e:
            return ""

    def request_stop(self):
        """Request script to stop"""
        self._stop_requested = True


class ScriptRunner:
    """Manages script execution in a sandboxed environment"""

    MAX_LOGS = 1000  # Maximum log entries to keep

    def __init__(self):
        self.state = ScriptState()
        self._thread: Optional[threading.Thread] = None
        self._bot_api: Optional[BotAPI] = None
        self._lock = threading.Lock()

    def _log(self, message: str):
        """Add a log entry"""
        timestamp = time.strftime("%H:%M:%S")
        with self._lock:
            self.state.logs.append(f"[{timestamp}] {message}")
            # Trim old logs
            if len(self.state.logs) > self.MAX_LOGS:
                self.state.logs = self.state.logs[-self.MAX_LOGS:]

    def load_script(self, code: str):
        """Load a script (doesn't start execution)"""
        with self._lock:
            self.state.script_code = code
            self.state.error = None

    def start(self) -> bool:
        """Start script execution"""
        with self._lock:
            if self.state.running:
                return False

            if not self.state.script_code:
                self.state.error = "No script loaded"
                return False

            self.state.running = True
            self.state.error = None
            self.state.logs = []
            self.state.started_at = time.time()

        self._bot_api = BotAPI(self)
        self._thread = threading.Thread(target=self._run_script, daemon=True)
        self._thread.start()
        self._log("Script started")
        return True

    def stop(self):
        """Stop script execution"""
        if self._bot_api:
            self._bot_api.request_stop()

        with self._lock:
            if self.state.running:
                self._log("Script stop requested")
            self.state.running = False

    def _run_script(self):
        """Execute the script in a sandboxed QuickJS context"""
        try:
            # Create QuickJS context
            ctx = quickjs.Context()

            # Set memory limit (no time limit - we handle stopping via API)
            ctx.set_memory_limit(50 * 1024 * 1024)  # 50MB

            # Create bot object with bound methods
            bot_api = self._bot_api

            # Register bot functions
            ctx.add_callable("_bot_sendCommand", lambda cmd: bot_api.send_command(cmd))
            ctx.add_callable("_bot_readTerminal", lambda lines=50: bot_api.read_terminal(int(lines)))
            ctx.add_callable("_bot_readChat", lambda lines=30: bot_api.read_chat(int(lines)))
            ctx.add_callable("_bot_sleep", lambda ms: bot_api.sleep(int(ms)))
            ctx.add_callable("_bot_log", lambda msg: bot_api.log(str(msg)))
            ctx.add_callable("_bot_getBalance", lambda: bot_api.get_balance())

            # Create bot wrapper object in JS
            wrapper_code = """
            const bot = {
                sendCommand: (cmd) => _bot_sendCommand(cmd),
                readTerminal: (lines) => _bot_readTerminal(lines || 50),
                readChat: (lines) => _bot_readChat(lines || 30),
                sleep: (ms) => _bot_sleep(ms),
                log: (msg) => _bot_log(msg),
                getBalance: () => _bot_getBalance()
            };

            // Alias for convenience
            const send = bot.sendCommand;
            const log = bot.log;
            const sleep = bot.sleep;
            """

            ctx.eval(wrapper_code)

            # Execute user script
            ctx.eval(self.state.script_code)

            self._log("Script completed successfully")

        except InterruptedError:
            self._log("Script stopped by user")
        except quickjs.JSException as e:
            error_msg = str(e)
            self._log(f"[ERROR] JavaScript error: {error_msg}")
            with self._lock:
                self.state.error = error_msg
        except Exception as e:
            error_msg = str(e)
            self._log(f"[ERROR] {error_msg}")
            with self._lock:
                self.state.error = error_msg
        finally:
            with self._lock:
                self.state.running = False

    def get_status(self) -> dict:
        """Get current script status"""
        with self._lock:
            return {
                'running': self.state.running,
                'has_script': bool(self.state.script_code),
                'error': self.state.error,
                'log_count': len(self.state.logs),
                'uptime': time.time() - self.state.started_at if self.state.started_at and self.state.running else 0
            }

    def get_logs(self, last_n: int = 100) -> list:
        """Get recent log entries"""
        with self._lock:
            return self.state.logs[-last_n:]

    def get_script(self) -> str:
        """Get current script code"""
        with self._lock:
            return self.state.script_code


# Global singleton instance
_runner_instance: Optional[ScriptRunner] = None

def get_runner() -> ScriptRunner:
    """Get the global script runner instance"""
    global _runner_instance
    if _runner_instance is None:
        _runner_instance = ScriptRunner()
    return _runner_instance


if __name__ == "__main__":
    # Test the script runner
    runner = get_runner()

    test_script = """
    log("Hello from script!");
    log("Reading terminal...");
    let terminal = bot.readTerminal(10);
    log("Terminal has " + terminal.length + " characters");

    for (let i = 0; i < 3; i++) {
        log("Loop iteration " + i);
        sleep(1000);
    }

    log("Script done!");
    """

    runner.load_script(test_script)
    runner.start()

    # Wait for script to complete
    time.sleep(10)

    print("\n=== Logs ===")
    for log in runner.get_logs():
        print(log)

    print("\n=== Status ===")
    print(runner.get_status())

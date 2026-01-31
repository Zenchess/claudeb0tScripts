"""Executes validated actions using existing infrastructure"""

import subprocess
import time
import asyncio
import sys
from pathlib import Path
from typing import Optional

from ..state.schemas import Action, ActionResult, ActionType


class ActionExecutor:
    """Executes validated actions using existing hackmud tools"""

    def __init__(self, project_root: str = "/home/jacob/hackmud"):
        self.project_root = Path(project_root)
        self.scanner = None  # Lazy-loaded Scanner instance
        self.last_command_time = 0
        self.command_rate_limit = 1.0  # Min seconds between commands

    def _get_scanner(self):
        """Get or create Scanner instance (lazy load)"""
        if self.scanner is None:
            try:
                # Add python_lib to path for Scanner import
                python_lib_path = str(self.project_root / "python_lib")
                if python_lib_path not in sys.path:
                    sys.path.insert(0, python_lib_path)

                from hackmud.memory import Scanner
                self.scanner = Scanner()
                self.scanner.connect()
            except Exception as e:
                print(f"Error loading Scanner: {e}")
                return None
        return self.scanner

    async def execute(self, action: Action) -> ActionResult:
        """
        Execute a validated action.

        Returns:
            ActionResult with success status and output
        """
        try:
            if action.action_type == ActionType.SHELL_COMMAND:
                return await self._execute_shell_command(action)
            elif action.action_type == ActionType.READ_GAME_STATE:
                return await self._read_game_state(action)
            elif action.action_type == ActionType.DISCORD_SEND:
                return await self._discord_send(action)
            elif action.action_type == ActionType.FILE_READ:
                return await self._file_read(action)
            elif action.action_type == ActionType.FILE_WRITE:
                return await self._file_write(action)
            else:
                return ActionResult(
                    success=False,
                    error=f"Unknown action type: {action.action_type}"
                )
        except Exception as e:
            return ActionResult(
                success=False,
                error=str(e)
            )

    async def _execute_shell_command(self, action: Action) -> ActionResult:
        """Execute bash/Python commands or hackmud scripts"""
        command = action.parameters.get('command', '')
        if not command:
            return ActionResult(success=False, error="No command specified")

        timeout = action.parameters.get('timeout', 30)

        try:
            # Rate limiting
            now = time.time()
            elapsed = now - self.last_command_time
            if elapsed < self.command_rate_limit:
                await asyncio.sleep(self.command_rate_limit - elapsed)

            # Check if it's a direct bash/python command (contains /, python3, etc)
            # vs a hackmud script name (no special characters, just word.word)
            is_bash_command = (
                '/' in command or
                command.startswith('python3') or
                command.startswith('bash') or
                command.startswith('ls') or
                command.startswith('grep') or
                command.startswith('cd ')
            )

            if is_bash_command:
                # Run as direct bash command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.project_root)
                )

                self.last_command_time = time.time()

                output = result.stdout
                if result.returncode != 0:
                    output = result.stderr or result.stdout

                return ActionResult(
                    success=result.returncode == 0,
                    output=output[:1000],
                    error=result.stderr[:500] if result.returncode != 0 else None
                )
            else:
                # Hackmud script - use send_command.py
                result = subprocess.run(
                    ['python3', str(self.project_root / 'send_command.py'), command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.project_root)
                )

                self.last_command_time = time.time()

                if result.returncode != 0:
                    return ActionResult(
                        success=False,
                        error=result.stderr[:500],
                        output=result.stdout[:500]
                    )

                # Wait for game to process
                await asyncio.sleep(2)

                # Read response from game
                game_output = await self._read_game_state(
                    Action(
                        action_type=ActionType.READ_GAME_STATE,
                        parameters={'window': 'shell', 'lines': 30}
                    )
                )

                return ActionResult(
                    success=True,
                    output=game_output.output[:1000] if game_output.output else '',
                    data={'command': command, 'response': game_output.data}
                )

        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                error=f"Command timed out after {timeout}s"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Error executing command: {str(e)[:500]}"
            )

    async def _read_game_state(self, action: Action) -> ActionResult:
        """Read game state using Scanner API"""
        try:
            scanner = self._get_scanner()
            if not scanner:
                # Don't treat "game offline" as a failure
                return ActionResult(
                    success=True,
                    output="[Game offline - Scanner not available]",
                    error=None,
                    data={'game_running': False}
                )

            window = action.parameters.get('window', 'shell')
            lines = action.parameters.get('lines', 30)

            # Read from game memory
            result = scanner.read_window(window, lines=lines)

            # Handle both string and list returns from scanner
            if isinstance(result, list):
                text = '\n'.join(result)
            else:
                text = result or ''

            return ActionResult(
                success=True,
                output=text,
                data={'window': window, 'content': text, 'lines': len(text.split('\n')) if text else 0}
            )

        except Exception as e:
            # On scanner error, try to reconnect
            self.scanner = None
            return ActionResult(
                success=False,
                error=f"Error reading game state: {e}"
            )

    async def _discord_send(self, action: Action) -> ActionResult:
        """Send message to Discord via discord_send_api.py"""
        try:
            channel_id = action.parameters.get('channel_id', '')
            message = action.parameters.get('message', '')
            file_path = action.parameters.get('file_path')

            if not channel_id or not message:
                return ActionResult(
                    success=False,
                    error="channel_id and message required"
                )

            # Build command
            cmd = [
                str(self.project_root / 'discord_send.sh'),
                channel_id,
                message
            ]

            # Add file attachment if provided
            if file_path:
                cmd.extend(['-a', file_path])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return ActionResult(
                    success=False,
                    error=result.stderr[:500]
                )

            return ActionResult(
                success=True,
                output=f"Message sent to channel {channel_id}",
                data={'channel_id': channel_id, 'message_length': len(message)}
            )

        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Error sending Discord message: {e}"
            )

    async def _file_read(self, action: Action) -> ActionResult:
        """Read a file"""
        try:
            file_path = action.parameters.get('file_path', '')
            if not file_path:
                return ActionResult(success=False, error="file_path required")

            path = Path(file_path).resolve()

            with open(path, 'r') as f:
                content = f.read()

            return ActionResult(
                success=True,
                output=content,
                data={'file_path': str(path), 'size': len(content)}
            )

        except FileNotFoundError:
            return ActionResult(
                success=False,
                error=f"File not found: {file_path}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Error reading file: {e}"
            )

    async def _file_write(self, action: Action) -> ActionResult:
        """Write a file"""
        try:
            file_path = action.parameters.get('file_path', '')
            content = action.parameters.get('content', '')
            append = action.parameters.get('append', False)

            if not file_path:
                return ActionResult(success=False, error="file_path required")

            path = Path(file_path).resolve()

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first
            tmp_path = path.with_suffix('.tmp')

            if append and path.exists():
                # Read existing content
                with open(path, 'r') as f:
                    existing = f.read()
                to_write = existing + content
            else:
                to_write = content

            # Write atomically
            with open(tmp_path, 'w') as f:
                f.write(to_write)

            tmp_path.replace(path)

            return ActionResult(
                success=True,
                output=f"File written: {path}",
                data={'file_path': str(path), 'size': len(to_write)}
            )

        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Error writing file: {e}"
            )

    def close(self) -> None:
        """Close Scanner connection"""
        if self.scanner:
            try:
                self.scanner.close()
            except:
                pass
            self.scanner = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

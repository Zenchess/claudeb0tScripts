"""Validates shell commands for safety"""

import re
from typing import Set, Tuple


class CommandValidator:
    """Validates shell commands against blocklist and suspicious patterns"""

    def __init__(self, blocked_commands: list = None):
        self.blocked_commands: Set[str] = set()
        if blocked_commands:
            # Normalize to lowercase
            self.blocked_commands = {cmd.lower() for cmd in blocked_commands}
        else:
            # Default blocklist
            self.blocked_commands = {
                'shutdown', 'quit', 'exit', 'logout', 'clear',
                'rm', 'rm -rf', 'format', 'dd', 'reboot', 'halt'
            }

        # Patterns that indicate shell redirection or piping (suspicious)
        self.suspicious_patterns = [
            (r'>+', 'output redirection'),
            (r'\|', 'piping'),
            (r'&&', 'command chaining'),
            (r';', 'command separator'),
            (r'\$\(', 'command substitution'),
            (r'`', 'backtick substitution'),
        ]

    def is_safe(self, command: str) -> Tuple[bool, str]:
        """
        Check if a command is safe to execute.

        Returns:
            (is_safe, reason) tuple
        """
        if not command or not isinstance(command, str):
            return False, "Empty or invalid command"

        # Extract main command (first word)
        parts = command.strip().split()
        if not parts:
            return False, "Empty command"

        main_cmd = parts[0].lower()

        # Check against blocklist
        if main_cmd in self.blocked_commands:
            return False, f"Blocked command: {main_cmd}"

        # Check for exact multi-word blocks (e.g., "rm -rf")
        cmd_start = ' '.join(parts[:2]).lower()
        if cmd_start in self.blocked_commands:
            return False, f"Blocked command: {cmd_start}"

        # Check for suspicious patterns
        for pattern, reason in self.suspicious_patterns:
            if re.search(pattern, command):
                # These are suspicious but allowed with approval
                return False, f"Suspicious pattern: {reason}"

        # Hackmud shell commands are safe
        # They follow pattern: script_name{arg1:value, arg2:value}
        # Or: user.script{args}
        return True, ""

    def is_safe_hackmud_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if a command is a safe hackmud script command.

        Hackmud commands follow patterns like:
        - sys.status
        - users.me
        - accts.balance
        - chats.tell{to:"user", msg:"hello"}
        """
        if not command or not isinstance(command, str):
            return False, "Empty or invalid command"

        command = command.strip()

        # Must contain at least one dot (user.script or builtin.script)
        if '.' not in command:
            return False, "Not a valid hackmud command (missing dot)"

        # Extract the script name part
        script_part = command.split('{')[0].strip()

        # Check against dangerous patterns
        if any(blocked in script_part.lower() for blocked in ['eval', 'exec', 'system']):
            return False, "Dangerous script"

        # All hackmud script commands are safe (game enforces permissions)
        return True, ""

    def validate_command_for_execution(self, command: str, is_hackmud_script: bool = False) -> Tuple[bool, str, bool]:
        """
        Validate a command for execution.

        Returns:
            (allowed, reason, requires_approval) tuple
        """
        if is_hackmud_script:
            # Hackmud commands are safe
            safe, reason = self.is_safe_hackmud_command(command)
            if not safe:
                return False, reason, False
            return True, "", False
        else:
            # Shell commands
            safe, reason = self.is_safe(command)
            if safe:
                return True, "", False
            else:
                # Suspicious but might be allowed with approval
                if 'suspicious' in reason.lower():
                    return False, reason, True
                else:
                    # Blocked commands require no approval
                    return False, reason, False

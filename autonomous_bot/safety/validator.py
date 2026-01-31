"""Main safety validator orchestrating all security checks"""

import json
from pathlib import Path
from typing import Tuple

from ..state.schemas import Action, ActionType, ValidationResult
from .command_validator import CommandValidator
from .file_validator import FileValidator
from .gc_validator import GCValidator
from .approval_queue import ApprovalQueue


class SafetyValidator:
    """Multi-layer safety validation for all bot actions"""

    def __init__(self, config_path: str = None):
        """Initialize safety validators from config"""
        # Load config
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "bot_config.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Initialize validators
        safety_config = self.config.get('safety', {})

        self.command_validator = CommandValidator(
            blocked_commands=safety_config.get('blocked_commands', [])
        )

        file_config = safety_config.get('file_operations', {})
        self.file_validator = FileValidator(
            allowed_base_path=file_config.get('allowed_base_path', '/home/jacob/hackmud'),
            protected_files=file_config.get('protected_files', []),
            protected_dirs=file_config.get('protected_dirs', []),
            max_file_size=file_config.get('max_file_size', 10_485_760)
        )

        gc_limits = safety_config.get('gc_limits', {})
        self.gc_validator = GCValidator(
            per_transaction_limit=gc_limits.get('per_transaction', 1_000_000),
            hourly_limit=gc_limits.get('hourly', 5_000_000),
            daily_limit=gc_limits.get('daily', 20_000_000)
        )

        self.approval_queue = ApprovalQueue()

        self.trusted_users = self.config.get('discord', {}).get('trusted_users', [])

    def _load_config(self) -> dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except:
            return {
                'safety': {
                    'blocked_commands': [],
                    'gc_limits': {},
                    'file_operations': {},
                    'emergency_stop': {}
                },
                'discord': {'trusted_users': []}
            }

    def validate_action(self, action: Action) -> ValidationResult:
        """
        Validate an action through all safety layers.

        Returns:
            ValidationResult with allowed, reason, and requires_approval fields
        """
        # Layer 1: Trust validation
        if action.triggered_by_discord and action.user_id:
            if action.user_id not in self.trusted_users:
                return ValidationResult(
                    allowed=False,
                    reason="User not in trusted list",
                    requires_approval=False,
                    severity="critical"
                )

        # Layer 2: Command validation
        if action.action_type == ActionType.SHELL_COMMAND:
            command = action.parameters.get('command', '')
            is_hackmud = action.parameters.get('is_hackmud_script', True)

            allowed, reason, needs_approval = self.command_validator.validate_command_for_execution(
                command, is_hackmud_script=is_hackmud
            )

            if not allowed:
                return ValidationResult(
                    allowed=False,
                    reason=reason,
                    requires_approval=needs_approval,
                    severity="warning" if needs_approval else "critical"
                )

        # Layer 3: File validation
        elif action.action_type == ActionType.FILE_READ:
            file_path = action.parameters.get('file_path', '')
            allowed, reason = self.file_validator.validate_read(file_path)

            if not allowed:
                return ValidationResult(
                    allowed=False,
                    reason=reason,
                    requires_approval=False,
                    severity="critical"
                )

        elif action.action_type == ActionType.FILE_WRITE:
            file_path = action.parameters.get('file_path', '')
            content = action.parameters.get('content', '')

            allowed, reason, needs_approval = self.file_validator.validate_write(file_path, content)

            if not allowed:
                return ValidationResult(
                    allowed=False,
                    reason=reason,
                    requires_approval=needs_approval,
                    severity="warning" if needs_approval else "critical"
                )

        # Layer 4: GC budget validation
        elif action.action_type == ActionType.APPROVE_ACTION:
            # Approval actions themselves don't need validation
            pass

        else:
            # Other action types (read_game_state, discord_send) are generally safe
            pass

        # All checks passed
        return ValidationResult(
            allowed=True,
            reason="",
            requires_approval=False,
            severity="info"
        )

    def queue_for_approval(self, action: Action) -> str:
        """Queue action for human approval, return action_id"""
        return self.approval_queue.add_action(action)

    def approve_action(self, action_id: str, approver_id: int) -> bool:
        """Approve a queued action"""
        return self.approval_queue.approve_action(action_id, approver_id)

    def reject_action(self, action_id: str, rejector_id: int, reason: str = "") -> bool:
        """Reject a queued action"""
        return self.approval_queue.reject_action(action_id, rejector_id, reason)

    def get_pending_approvals(self) -> dict:
        """Get all actions awaiting approval"""
        return self.approval_queue.get_pending_actions()

    def can_execute(self, action_id: str) -> bool:
        """Check if a queued action has been approved"""
        return self.approval_queue.is_approved(action_id)

    def get_budget_status(self) -> dict:
        """Get current GC budget status"""
        return self.gc_validator.get_budget_status()

    def record_transaction(self, amount: int) -> bool:
        """Record a GC transaction"""
        return self.gc_validator.record_transaction(amount)

    def is_safe_command(self, command: str, is_hackmud: bool = True) -> bool:
        """Quick check: is this command safe?"""
        if is_hackmud:
            safe, _ = self.command_validator.is_safe_hackmud_command(command)
        else:
            safe, _ = self.command_validator.is_safe(command)
        return safe

    def is_safe_file_path(self, file_path: str) -> bool:
        """Quick check: is this file path safe?"""
        safe, _ = self.file_validator.is_safe_path(file_path)
        return safe

    def is_within_gc_budget(self, amount: int) -> bool:
        """Quick check: is this GC amount within budget?"""
        return self.gc_validator.is_within_budget(amount)

    def get_safety_summary(self) -> dict:
        """Get summary of all safety systems"""
        return {
            'budget': self.get_budget_status(),
            'pending_approvals': self.approval_queue.get_summary(),
            'trusted_users': len(self.trusted_users),
            'blocked_commands': len(self.command_validator.blocked_commands)
        }

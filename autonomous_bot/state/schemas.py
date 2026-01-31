"""Data classes and schemas for autonomous bot state and actions"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import json


class ActionType(Enum):
    """Types of actions the bot can execute"""
    SHELL_COMMAND = "shell_command"
    READ_GAME_STATE = "read_game_state"
    DISCORD_SEND = "discord_send"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    APPROVE_ACTION = "approve_action"


class GameEventType(Enum):
    """Types of events detected in game output"""
    TELL = "tell"
    GC_TRANSFER = "gc_transfer"
    BREACH_SUCCESS = "breach_success"
    LOCK_BREACHED = "lock_breached"
    NPC_ENGAGED = "npc_engaged"
    LEVEL_UP = "level_up"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of action validation"""
    allowed: bool
    reason: str = ""
    requires_approval: bool = False
    severity: str = "info"  # info, warning, critical


@dataclass
class ActionResult:
    """Result of executing an action"""
    success: bool
    output: str = ""
    error: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Action:
    """Represents a planned action to execute"""
    action_type: ActionType
    parameters: Dict[str, Any]
    reasoning: str = ""
    priority: str = "normal"  # critical, high, normal, low
    action_id: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    triggered_by_discord: bool = False
    user_id: Optional[int] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d['action_type'] = self.action_type.value
        return d


@dataclass
class Decision:
    """AI decision containing planned actions"""
    reasoning: str
    actions: List[Action] = field(default_factory=list)
    confidence: float = 0.5
    alternatives: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        return {
            'reasoning': self.reasoning,
            'actions': [a.to_dict() for a in self.actions],
            'confidence': self.confidence,
            'alternatives': self.alternatives,
            'created_at': self.created_at
        }


@dataclass
class GameState:
    """Snapshot of current game state"""
    shell_output: str = ""
    chat_output: str = ""
    balance: int = 0
    location: str = "unknown"
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    version: str = ""
    active_scripts: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GameEvent:
    """Event detected in game"""
    event_type: GameEventType
    data: Dict[str, Any]
    raw_text: str = ""
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        d = asdict(self)
        d['event_type'] = self.event_type.value
        return d


@dataclass
class DiscordMessage:
    """Message from Discord"""
    user_id: int
    username: str
    display_name: str
    content: str
    timestamp: str
    is_dm: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Task:
    """Task for bot to execute"""
    task_id: str
    description: str
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    timeout: float = 300  # 5 minutes default
    created_by_user_id: Optional[int] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None

    def is_expired(self) -> bool:
        return (datetime.now().timestamp() - self.created_at) > self.timeout

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BudgetStatus:
    """Track GC spending"""
    per_transaction_limit: int = 1_000_000
    hourly_limit: int = 5_000_000
    daily_limit: int = 20_000_000

    gc_spent_this_transaction: int = 0
    gc_spent_this_hour: int = 0
    gc_spent_today: int = 0

    hourly_reset_time: float = field(default_factory=lambda: datetime.now().timestamp())
    daily_reset_time: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BotState:
    """Complete persistent state of the bot"""
    # Operational state
    running: bool = True
    last_heartbeat: float = field(default_factory=lambda: datetime.now().timestamp())
    emergency_stop: bool = False
    emergency_stop_reason: str = ""

    # Game state
    current_balance: int = 0
    current_location: str = "unknown"
    active_tasks: List[Task] = field(default_factory=list)

    # Discord state
    last_discord_message_id: str = ""
    pending_responses: List[str] = field(default_factory=list)

    # Budget tracking
    budget: BudgetStatus = field(default_factory=BudgetStatus)

    # Safety tracking
    failed_actions: int = 0
    last_error_time: float = 0
    error_count_in_window: int = 0

    # Statistics
    total_actions_executed: int = 0
    total_commands_sent: int = 0
    total_errors: int = 0
    uptime_seconds: float = 0

    # Internal
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    last_updated: float = field(default_factory=lambda: datetime.now().timestamp())

    @staticmethod
    def default() -> 'BotState':
        return BotState()

    def to_dict(self) -> dict:
        return {
            'running': self.running,
            'last_heartbeat': self.last_heartbeat,
            'emergency_stop': self.emergency_stop,
            'emergency_stop_reason': self.emergency_stop_reason,
            'current_balance': self.current_balance,
            'current_location': self.current_location,
            'active_tasks': [t.to_dict() for t in self.active_tasks],
            'last_discord_message_id': self.last_discord_message_id,
            'pending_responses': self.pending_responses,
            'budget': self.budget.to_dict(),
            'failed_actions': self.failed_actions,
            'last_error_time': self.last_error_time,
            'error_count_in_window': self.error_count_in_window,
            'total_actions_executed': self.total_actions_executed,
            'total_commands_sent': self.total_commands_sent,
            'total_errors': self.total_errors,
            'uptime_seconds': self.uptime_seconds,
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }

    @staticmethod
    def from_dict(data: dict) -> 'BotState':
        """Load state from dict, with safe defaults"""
        try:
            # Convert task dicts back to Task objects
            tasks = []
            for t in data.get('active_tasks', []):
                if isinstance(t, dict):
                    tasks.append(Task(
                        task_id=t.get('task_id', ''),
                        description=t.get('description', ''),
                        created_at=t.get('created_at', 0),
                        timeout=t.get('timeout', 300),
                        created_by_user_id=t.get('created_by_user_id'),
                        status=t.get('status', 'pending'),
                        result=t.get('result')
                    ))

            # Convert budget dict back to BudgetStatus
            budget_data = data.get('budget', {})
            budget = BudgetStatus(
                per_transaction_limit=budget_data.get('per_transaction_limit', 1_000_000),
                hourly_limit=budget_data.get('hourly_limit', 5_000_000),
                daily_limit=budget_data.get('daily_limit', 20_000_000),
                gc_spent_this_transaction=budget_data.get('gc_spent_this_transaction', 0),
                gc_spent_this_hour=budget_data.get('gc_spent_this_hour', 0),
                gc_spent_today=budget_data.get('gc_spent_today', 0),
                hourly_reset_time=budget_data.get('hourly_reset_time', 0),
                daily_reset_time=budget_data.get('daily_reset_time', 0)
            )

            return BotState(
                running=data.get('running', True),
                last_heartbeat=data.get('last_heartbeat', 0),
                emergency_stop=data.get('emergency_stop', False),
                emergency_stop_reason=data.get('emergency_stop_reason', ''),
                current_balance=data.get('current_balance', 0),
                current_location=data.get('current_location', 'unknown'),
                active_tasks=tasks,
                last_discord_message_id=data.get('last_discord_message_id', ''),
                pending_responses=data.get('pending_responses', []),
                budget=budget,
                failed_actions=data.get('failed_actions', 0),
                last_error_time=data.get('last_error_time', 0),
                error_count_in_window=data.get('error_count_in_window', 0),
                total_actions_executed=data.get('total_actions_executed', 0),
                total_commands_sent=data.get('total_commands_sent', 0),
                total_errors=data.get('total_errors', 0),
                uptime_seconds=data.get('uptime_seconds', 0),
                created_at=data.get('created_at', 0),
                last_updated=data.get('last_updated', 0)
            )
        except Exception as e:
            print(f"Error loading state from dict: {e}, using defaults")
            return BotState.default()

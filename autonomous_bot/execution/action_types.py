"""Action types and definitions for autonomous bot"""

from enum import Enum


class ActionType(Enum):
    """Types of actions the bot can perform"""
    SHELL_COMMAND = "shell_command"
    READ_GAME_STATE = "read_game_state"
    DISCORD_SEND = "discord_send"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    APPROVE_ACTION = "approve_action"


# Action parameter schemas for reference
ACTION_SCHEMAS = {
    'shell_command': {
        'command': 'str - hackmud script or command to execute',
        'is_hackmud_script': 'bool - whether this is a hackmud script (True) or shell command (False)',
        'timeout': 'int - max seconds to wait for response (default 10)'
    },
    'read_game_state': {
        'window': 'str - which window to read (shell, chat, badge, breach, scratch)',
        'lines': 'int - number of lines to read (default 30)'
    },
    'discord_send': {
        'channel_id': 'str - Discord channel ID',
        'message': 'str - message text to send',
        'file_path': 'str (optional) - path to file to attach'
    },
    'file_read': {
        'file_path': 'str - path to file to read'
    },
    'file_write': {
        'file_path': 'str - path to file to write',
        'content': 'str - content to write',
        'append': 'bool - whether to append (True) or overwrite (False)'
    },
    'approve_action': {
        'action_id': 'str - ID of action to approve',
        'approver_id': 'int - Discord user ID of approver'
    }
}

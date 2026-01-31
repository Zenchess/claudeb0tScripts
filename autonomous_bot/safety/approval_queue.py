"""Manages approval queue for high-risk actions"""

import json
import time
import uuid
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from ..state.schemas import Action


class ApprovalQueue:
    """Manages high-risk actions awaiting human approval"""

    def __init__(self, queue_file: Optional[Path] = None):
        if queue_file is None:
            queue_file = Path(__file__).parent.parent / "state" / "approval_queue.json"

        self.queue_file = Path(queue_file)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

        self.approval_timeout = 300  # 5 minutes default

    def _load_queue(self) -> dict:
        """Load approval queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'pending': {}, 'approved': {}, 'rejected': {}}

    def _save_queue(self, queue: dict) -> None:
        """Save approval queue to file"""
        try:
            tmp_file = self.queue_file.with_suffix('.tmp')
            with open(tmp_file, 'w') as f:
                json.dump(queue, f, indent=2)
            tmp_file.replace(self.queue_file)
        except Exception as e:
            print(f"Error saving approval queue: {e}")

    def add_action(self, action: Action) -> str:
        """
        Add an action to the approval queue.

        Returns:
            action_id
        """
        action_id = str(uuid.uuid4())[:8]

        queue = self._load_queue()
        queue['pending'][action_id] = {
            'action': action.to_dict(),
            'created_at': datetime.now().isoformat(),
            'expires_at': datetime.fromtimestamp(
                time.time() + self.approval_timeout
            ).isoformat()
        }

        self._save_queue(queue)
        return action_id

    def approve_action(self, action_id: str, approver_id: int) -> bool:
        """Approve a pending action"""
        queue = self._load_queue()

        if action_id not in queue['pending']:
            return False

        pending = queue['pending'].pop(action_id)
        pending['approved_by'] = approver_id
        pending['approved_at'] = datetime.now().isoformat()

        queue['approved'][action_id] = pending
        self._save_queue(queue)
        return True

    def reject_action(self, action_id: str, rejector_id: int, reason: str = "") -> bool:
        """Reject a pending action"""
        queue = self._load_queue()

        if action_id not in queue['pending']:
            return False

        pending = queue['pending'].pop(action_id)
        pending['rejected_by'] = rejector_id
        pending['rejected_at'] = datetime.now().isoformat()
        pending['rejection_reason'] = reason

        queue['rejected'][action_id] = pending
        self._save_queue(queue)
        return True

    def get_pending_actions(self) -> Dict[str, dict]:
        """Get all pending actions, removing expired ones"""
        queue = self._load_queue()
        now = datetime.now()

        # Remove expired actions
        expired = []
        for action_id, action_data in queue['pending'].items():
            expires_at = datetime.fromisoformat(action_data['expires_at'])
            if now > expires_at:
                expired.append(action_id)

        # Move expired to rejected
        for action_id in expired:
            action = queue['pending'].pop(action_id)
            action['rejected_at'] = now.isoformat()
            action['rejection_reason'] = 'Timeout - no approval received'
            queue['rejected'][action_id] = action

        self._save_queue(queue)

        return queue['pending']

    def is_approved(self, action_id: str) -> bool:
        """Check if an action has been approved"""
        queue = self._load_queue()
        return action_id in queue['approved']

    def is_rejected(self, action_id: str) -> bool:
        """Check if an action has been rejected"""
        queue = self._load_queue()
        return action_id in queue['rejected']

    def is_pending(self, action_id: str) -> bool:
        """Check if an action is still pending"""
        queue = self._load_queue()
        return action_id in queue['pending']

    def get_action(self, action_id: str) -> Optional[dict]:
        """Get action details"""
        queue = self._load_queue()

        for status_dict in [queue['pending'], queue['approved'], queue['rejected']]:
            if action_id in status_dict:
                return status_dict[action_id]

        return None

    def clear_old_actions(self, days: int = 7) -> int:
        """Remove approved/rejected actions older than N days"""
        queue = self._load_queue()
        now = datetime.now()
        cutoff = now.timestamp() - (days * 24 * 60 * 60)

        removed = 0

        # Clean approved
        to_remove = []
        for action_id, action_data in queue['approved'].items():
            created_at = datetime.fromisoformat(action_data['created_at']).timestamp()
            if created_at < cutoff:
                to_remove.append(action_id)

        for action_id in to_remove:
            del queue['approved'][action_id]
            removed += 1

        # Clean rejected
        to_remove = []
        for action_id, action_data in queue['rejected'].items():
            created_at = datetime.fromisoformat(action_data['created_at']).timestamp()
            if created_at < cutoff:
                to_remove.append(action_id)

        for action_id in to_remove:
            del queue['rejected'][action_id]
            removed += 1

        self._save_queue(queue)
        return removed

    def get_summary(self) -> dict:
        """Get summary of queue status"""
        queue = self._load_queue()

        # Clean expired first
        self.get_pending_actions()
        queue = self._load_queue()

        return {
            'pending_count': len(queue['pending']),
            'approved_count': len(queue['approved']),
            'rejected_count': len(queue['rejected']),
            'pending_actions': list(queue['pending'].keys())
        }

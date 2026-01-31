"""Validates GC (game currency) spending against budgets"""

import time
from typing import Tuple


class GCValidator:
    """Validates GC transactions against budget limits"""

    def __init__(self, per_transaction_limit: int = 1_000_000,
                 hourly_limit: int = 5_000_000,
                 daily_limit: int = 20_000_000):

        self.per_transaction_limit = per_transaction_limit
        self.hourly_limit = hourly_limit
        self.daily_limit = daily_limit

        # Runtime tracking
        self.gc_spent_this_transaction = 0
        self.gc_spent_this_hour = 0
        self.gc_spent_today = 0

        self.hourly_reset_time = time.time()
        self.daily_reset_time = time.time()

    def _reset_hourly_if_needed(self) -> None:
        """Reset hourly counter if an hour has passed"""
        now = time.time()
        if now - self.hourly_reset_time > 3600:  # 1 hour
            self.gc_spent_this_hour = 0
            self.hourly_reset_time = now

    def _reset_daily_if_needed(self) -> None:
        """Reset daily counter if a day has passed"""
        now = time.time()
        if now - self.daily_reset_time > 86400:  # 24 hours
            self.gc_spent_today = 0
            self.daily_reset_time = now

    def validate_transaction(self, amount: int) -> Tuple[bool, str]:
        """
        Validate a GC transaction amount.

        Returns:
            (allowed, reason) tuple
        """
        # Check for invalid amounts
        if amount <= 0:
            return False, "Transaction amount must be positive"

        if amount > 1_000_000_000:  # 1B GC
            return False, "Transaction amount suspiciously large"

        # Reset counters if needed
        self._reset_hourly_if_needed()
        self._reset_daily_if_needed()

        # Check per-transaction limit
        if amount > self.per_transaction_limit:
            return False, f"Amount {amount} exceeds per-transaction limit {self.per_transaction_limit}"

        # Check hourly limit
        if self.gc_spent_this_hour + amount > self.hourly_limit:
            remaining = self.hourly_limit - self.gc_spent_this_hour
            return False, f"Would exceed hourly limit ({remaining} remaining)"

        # Check daily limit
        if self.gc_spent_today + amount > self.daily_limit:
            remaining = self.daily_limit - self.gc_spent_today
            return False, f"Would exceed daily limit ({remaining} remaining)"

        return True, ""

    def record_transaction(self, amount: int) -> bool:
        """Record a GC transaction (should only be called after validation)"""
        # Reset counters if needed
        self._reset_hourly_if_needed()
        self._reset_daily_if_needed()

        self.gc_spent_this_transaction = amount
        self.gc_spent_this_hour += amount
        self.gc_spent_today += amount
        return True

    def get_budget_status(self) -> dict:
        """Get current budget status"""
        self._reset_hourly_if_needed()
        self._reset_daily_if_needed()

        now = time.time()

        return {
            'per_transaction': {
                'limit': self.per_transaction_limit,
                'spent_this_transaction': self.gc_spent_this_transaction,
                'remaining': self.per_transaction_limit - self.gc_spent_this_transaction
            },
            'hourly': {
                'limit': self.hourly_limit,
                'spent': self.gc_spent_this_hour,
                'remaining': self.hourly_limit - self.gc_spent_this_hour,
                'time_until_reset': 3600 - (now - self.hourly_reset_time)
            },
            'daily': {
                'limit': self.daily_limit,
                'spent': self.gc_spent_today,
                'remaining': self.daily_limit - self.gc_spent_today,
                'time_until_reset': 86400 - (now - self.daily_reset_time)
            }
        }

    def is_within_budget(self, amount: int) -> bool:
        """Quick check: is this amount within all budgets?"""
        allowed, _ = self.validate_transaction(amount)
        return allowed

    def reset_all(self) -> None:
        """Emergency reset of all counters"""
        now = time.time()
        self.gc_spent_this_transaction = 0
        self.gc_spent_this_hour = 0
        self.gc_spent_today = 0
        self.hourly_reset_time = now
        self.daily_reset_time = now

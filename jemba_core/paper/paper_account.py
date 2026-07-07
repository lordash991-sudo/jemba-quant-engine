from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PaperAccountState:
    balance: float
    equity: float
    used_margin: float
    realized_pnl: float
    unrealized_pnl: float


class PaperAccount:

    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.used_margin = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

    @property
    def equity(self) -> float:
        return self.balance + self.unrealized_pnl

    @property
    def free_margin(self) -> float:
        return self.equity - self.used_margin

    def reserve_margin(self, amount: float) -> bool:
        if amount <= 0:
            return False

        if amount > self.free_margin:
            return False

        self.used_margin += amount
        return True

    def release_margin(self, amount: float) -> None:
        self.used_margin = max(0.0, self.used_margin - amount)

    def apply_realized_pnl(self, pnl: float) -> None:
        self.realized_pnl += pnl
        self.balance += pnl

    def update_unrealized_pnl(self, pnl: float) -> None:
        self.unrealized_pnl = pnl

    def state(self) -> PaperAccountState:
        return PaperAccountState(
            balance=self.balance,
            equity=self.equity,
            used_margin=self.used_margin,
            realized_pnl=self.realized_pnl,
            unrealized_pnl=self.unrealized_pnl,
        )

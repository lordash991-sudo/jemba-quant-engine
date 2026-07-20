from __future__ import annotations

import math

from jemba_core.paper_broker.models import AccountSnapshot
from jemba_core.paper_broker.position import PaperPosition


class PaperAccount:
    def __init__(
        self,
        initial_balance: float = 10_000.0,
    ) -> None:
        try:
            numeric = float(initial_balance)
        except (TypeError, ValueError) as exc:
            raise TypeError("INITIAL_BALANCE_MUST_BE_NUMERIC") from exc

        if not math.isfinite(numeric):
            raise ValueError("INITIAL_BALANCE_MUST_BE_FINITE")

        if numeric <= 0.0:
            raise ValueError("INITIAL_BALANCE_MUST_BE_POSITIVE")

        self.initial_balance = numeric
        self.cash_balance = numeric
        self.realized_pnl = 0.0

    def reserve_margin(
        self,
        position: PaperPosition,
        existing_positions: tuple[PaperPosition, ...],
    ) -> None:
        required_margin = position.margin_used
        free_margin = self.free_margin(existing_positions)

        if required_margin > free_margin:
            raise ValueError("INSUFFICIENT_FREE_MARGIN")

    def apply_closed_position(
        self,
        position: PaperPosition,
    ) -> None:
        self.realized_pnl += position.realized_pnl
        self.cash_balance += position.realized_pnl

    def used_margin(
        self,
        positions: tuple[PaperPosition, ...],
    ) -> float:
        return float(sum(position.margin_used for position in positions))

    def unrealized_pnl(
        self,
        positions: tuple[PaperPosition, ...],
    ) -> float:
        return float(sum(position.unrealized_pnl for position in positions))

    def equity(
        self,
        positions: tuple[PaperPosition, ...],
    ) -> float:
        return float(self.cash_balance + self.unrealized_pnl(positions))

    def free_margin(
        self,
        positions: tuple[PaperPosition, ...],
    ) -> float:
        return float(self.equity(positions) - self.used_margin(positions))

    def snapshot(
        self,
        open_positions: tuple[PaperPosition, ...],
        closed_positions: tuple[PaperPosition, ...],
    ) -> AccountSnapshot:
        used_margin = self.used_margin(open_positions)
        unrealized_pnl = self.unrealized_pnl(open_positions)
        equity = self.equity(open_positions)

        return AccountSnapshot(
            initial_balance=float(self.initial_balance),
            cash_balance=float(self.cash_balance),
            equity=float(equity),
            used_margin=float(used_margin),
            free_margin=float(equity - used_margin),
            unrealized_pnl=float(unrealized_pnl),
            realized_pnl=float(self.realized_pnl),
            open_positions=len(open_positions),
            closed_positions=len(closed_positions),
        )

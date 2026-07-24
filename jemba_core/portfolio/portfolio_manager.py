from __future__ import annotations

from typing import Any


class PortfolioManager:
    def __init__(
        self,
        account_balance: float = 10000.0,
        risk_per_trade: float = 0.01,
        max_positions: int = 1,
    ) -> None:
        if account_balance <= 0:
            raise ValueError("ACCOUNT_BALANCE_MUST_BE_POSITIVE")

        if not 0 < risk_per_trade <= 1:
            raise ValueError("RISK_PER_TRADE_MUST_BE_BETWEEN_0_AND_1")

        if max_positions <= 0:
            raise ValueError("MAX_POSITIONS_MUST_BE_POSITIVE")

        self.account_balance = float(account_balance)
        self.risk_per_trade = float(risk_per_trade)
        self.max_positions = int(max_positions)
        self.open_positions: list[dict[str, Any]] = []

    @property
    def risk_amount(self) -> float:
        return self.account_balance * self.risk_per_trade

    def can_open_position(self) -> bool:
        return len(self.open_positions) < self.max_positions

    def calculate_position_size(
        self,
        entry: float,
        stop_loss: float,
    ) -> float:
        entry = float(entry)
        stop_loss = float(stop_loss)

        if entry <= 0:
            raise ValueError("ENTRY_MUST_BE_POSITIVE")

        risk_per_unit = abs(entry - stop_loss)

        if risk_per_unit <= 0:
            return 0.0

        return round(
            self.risk_amount / risk_per_unit,
            6,
        )

    def register_position(
        self,
        position: dict[str, Any],
    ) -> bool:
        if not isinstance(position, dict):
            raise TypeError("POSITION_MUST_BE_DICT")

        if not self.can_open_position():
            return False

        self.open_positions.append(
            dict(position)
        )

        return True

    def close_position(
        self,
        pnl: float,
    ) -> bool:
        if not self.open_positions:
            return False

        self.open_positions.pop(0)
        self.account_balance += float(pnl)

        return True

    def reset(self) -> None:
        self.open_positions.clear()

    def summary(self) -> dict[str, Any]:
        return {
            "account_balance": self.account_balance,
            "risk_per_trade": self.risk_per_trade,
            "risk_amount": self.risk_amount,
            "max_positions": self.max_positions,
            "open_positions": len(self.open_positions),
            "can_open_position": self.can_open_position(),
        }

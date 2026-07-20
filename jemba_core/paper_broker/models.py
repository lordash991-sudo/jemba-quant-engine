from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PositionSide(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class CloseReason(StrEnum):
    MANUAL = "MANUAL"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


@dataclass(frozen=True, slots=True)
class PositionSnapshot:
    position_id: str
    symbol: str
    side: PositionSide
    status: PositionStatus

    entry_price: float
    current_price: float
    quantity: float
    leverage: int

    stop_loss: float
    take_profit: float

    notional: float
    margin_used: float

    unrealized_pnl: float
    realized_pnl: float

    open_commission: float
    close_commission: float

    opened_at: datetime
    closed_at: datetime | None
    close_reason: CloseReason | None


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    initial_balance: float
    cash_balance: float
    equity: float

    used_margin: float
    free_margin: float

    unrealized_pnl: float
    realized_pnl: float

    open_positions: int
    closed_positions: int

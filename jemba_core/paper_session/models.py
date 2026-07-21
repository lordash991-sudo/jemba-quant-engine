from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from jemba_core.paper_broker import (
    AccountSnapshot,
    PositionSide,
    PositionSnapshot,
    TradeManagementEvent,
)


class PaperSessionStatus(StrEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"


class PaperSessionEventType(StrEnum):
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_STOPPED = "SESSION_STOPPED"
    PRICE_UPDATED = "PRICE_UPDATED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_REJECTED = "POSITION_REJECTED"
    POSITION_CLOSED = "POSITION_CLOSED"
    KILL_SWITCH_ACTIVATED = "KILL_SWITCH_ACTIVATED"


@dataclass(frozen=True, slots=True)
class MarketPriceUpdate:
    symbol: str
    price: float
    timestamp: datetime

    def __post_init__(self) -> None:
        normalized_symbol = self.symbol.strip().upper()

        if not normalized_symbol:
            raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

        numeric_price = _positive_finite(
            self.price,
            "PRICE",
        )

        if self.timestamp.tzinfo is None:
            raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")

        object.__setattr__(
            self,
            "symbol",
            normalized_symbol,
        )
        object.__setattr__(
            self,
            "price",
            numeric_price,
        )


@dataclass(frozen=True, slots=True)
class PaperTradeRequest:
    symbol: str
    side: PositionSide

    entry_price: float
    quantity: float
    leverage: int

    stop_loss: float
    take_profit: float

    commission: float = 0.0

    def __post_init__(self) -> None:
        normalized_symbol = self.symbol.strip().upper()

        if not normalized_symbol:
            raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

        if not isinstance(self.side, PositionSide):
            raise TypeError("SIDE_MUST_BE_POSITION_SIDE")

        object.__setattr__(
            self,
            "symbol",
            normalized_symbol,
        )

        for field_name, field_value in (
            ("ENTRY_PRICE", self.entry_price),
            ("QUANTITY", self.quantity),
            ("STOP_LOSS", self.stop_loss),
            ("TAKE_PROFIT", self.take_profit),
        ):
            _positive_finite(
                field_value,
                field_name,
            )

        _non_negative_finite(
            self.commission,
            "COMMISSION",
        )

        if not isinstance(self.leverage, int):
            raise TypeError("LEVERAGE_MUST_BE_INTEGER")

        if self.leverage <= 0:
            raise ValueError("LEVERAGE_MUST_BE_POSITIVE")


@dataclass(frozen=True, slots=True)
class PaperSessionEvent:
    event_type: PaperSessionEventType
    timestamp: datetime

    symbol: str | None = None
    position_id: str | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class PaperSessionSnapshot:
    session_id: str
    status: PaperSessionStatus

    started_at: datetime | None
    stopped_at: datetime | None

    processed_price_updates: int
    opened_positions: int
    rejected_positions: int
    management_events: int

    account: AccountSnapshot
    open_positions: tuple[PositionSnapshot, ...]
    closed_positions: tuple[PositionSnapshot, ...]
    events: tuple[PaperSessionEvent, ...]


@dataclass(frozen=True, slots=True)
class PaperSessionUpdateResult:
    price_update: MarketPriceUpdate
    management_events: tuple[TradeManagementEvent, ...]
    session_snapshot: PaperSessionSnapshot


def _positive_finite(
    value: float,
    name: str,
) -> float:
    numeric = _finite_float(value, name)

    if numeric <= 0.0:
        raise ValueError(f"{name}_MUST_BE_POSITIVE")

    return numeric


def _non_negative_finite(
    value: float,
    name: str,
) -> float:
    numeric = _finite_float(value, name)

    if numeric < 0.0:
        raise ValueError(f"{name}_MUST_BE_NON_NEGATIVE")

    return numeric


def _finite_float(
    value: float,
    name: str,
) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name}_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name}_MUST_BE_FINITE")

    return numeric

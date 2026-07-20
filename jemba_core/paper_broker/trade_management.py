from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TradeManagementEventType(StrEnum):
    BREAK_EVEN = "BREAK_EVEN"
    PARTIAL_TAKE_PROFIT = "PARTIAL_TAKE_PROFIT"
    TRAILING_STOP = "TRAILING_STOP"
    TIME_STOP = "TIME_STOP"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


@dataclass(frozen=True, slots=True)
class TradeManagementConfig:
    break_even_trigger_rr: float = 1.0
    break_even_offset_rr: float = 0.0

    partial_take_profit_trigger_rr: float = 1.0
    partial_take_profit_fraction: float = 0.50

    trailing_stop_trigger_rr: float = 1.50
    trailing_stop_distance_rr: float = 0.50

    maximum_hold_minutes: float | None = None

    def __post_init__(self) -> None:
        _positive_finite(
            self.break_even_trigger_rr,
            "BREAK_EVEN_TRIGGER_RR",
        )

        _non_negative_finite(
            self.break_even_offset_rr,
            "BREAK_EVEN_OFFSET_RR",
        )

        _positive_finite(
            self.partial_take_profit_trigger_rr,
            "PARTIAL_TAKE_PROFIT_TRIGGER_RR",
        )

        partial_fraction = _finite_float(
            self.partial_take_profit_fraction,
            "PARTIAL_TAKE_PROFIT_FRACTION",
        )

        if not 0.0 < partial_fraction < 1.0:
            raise ValueError("PARTIAL_TAKE_PROFIT_FRACTION_MUST_BE_BETWEEN_0_AND_1")

        _positive_finite(
            self.trailing_stop_trigger_rr,
            "TRAILING_STOP_TRIGGER_RR",
        )

        _positive_finite(
            self.trailing_stop_distance_rr,
            "TRAILING_STOP_DISTANCE_RR",
        )

        if self.maximum_hold_minutes is not None:
            _positive_finite(
                self.maximum_hold_minutes,
                "MAXIMUM_HOLD_MINUTES",
            )


@dataclass(slots=True)
class ManagedPositionState:
    position_id: str
    initial_quantity: float
    initial_stop_loss: float
    risk_distance: float

    highest_price: float
    lowest_price: float

    break_even_applied: bool = False
    partial_take_profit_applied: bool = False
    trailing_stop_active: bool = False


@dataclass(frozen=True, slots=True)
class TradeManagementEvent:
    event_type: TradeManagementEventType

    position_id: str
    symbol: str

    price: float
    quantity: float

    realized_pnl: float = 0.0
    new_stop_loss: float | None = None

    timestamp: datetime | None = None


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

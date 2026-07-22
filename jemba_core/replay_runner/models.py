from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from jemba_core.market_replay import Candle
from jemba_core.paper_broker import PositionSide


class ReplaySignalAction(StrEnum):
    HOLD = "HOLD"
    OPEN = "OPEN"


class ReplayRunnerStatus(StrEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


@dataclass(frozen=True, slots=True)
class ReplayTradeSignal:
    symbol: str
    side: PositionSide

    confidence: float
    quantity: float
    leverage: int

    stop_loss: float
    take_profit: float

    commission: float = 0.0
    reason: str | None = None

    def __post_init__(self) -> None:
        normalized_symbol = self.symbol.strip().upper()

        if not normalized_symbol:
            raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

        if not isinstance(self.side, PositionSide):
            raise TypeError("SIDE_MUST_BE_POSITION_SIDE")

        confidence = _finite_float(
            self.confidence,
            "CONFIDENCE",
        )

        if not 0.0 <= confidence <= 100.0:
            raise ValueError("CONFIDENCE_MUST_BE_BETWEEN_0_AND_100")

        quantity = _positive_finite(
            self.quantity,
            "QUANTITY",
        )
        stop_loss = _positive_finite(
            self.stop_loss,
            "STOP_LOSS",
        )
        take_profit = _positive_finite(
            self.take_profit,
            "TAKE_PROFIT",
        )
        commission = _non_negative_finite(
            self.commission,
            "COMMISSION",
        )

        if not isinstance(self.leverage, int):
            raise TypeError("LEVERAGE_MUST_BE_INTEGER")

        if self.leverage <= 0:
            raise ValueError("LEVERAGE_MUST_BE_POSITIVE")

        object.__setattr__(
            self,
            "symbol",
            normalized_symbol,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "quantity",
            quantity,
        )
        object.__setattr__(
            self,
            "stop_loss",
            stop_loss,
        )
        object.__setattr__(
            self,
            "take_profit",
            take_profit,
        )
        object.__setattr__(
            self,
            "commission",
            commission,
        )


@dataclass(frozen=True, slots=True)
class ReplayStrategyContext:
    candle: Candle
    candle_index: int
    symbol_candle_index: int

    has_open_position: bool
    account_equity: float
    free_margin: float

    previous_candle: Candle | None = None


@dataclass(frozen=True, slots=True)
class ReplaySignalRecord:
    candle_index: int
    timestamp: datetime
    symbol: str

    action: ReplaySignalAction
    confidence: float | None

    approved: bool
    position_id: str | None
    reason: str | None


@dataclass(frozen=True, slots=True)
class ReplayRunnerStatistics:
    processed_candles: int
    generated_signals: int

    approved_signals: int
    rejected_signals: int
    hold_events: int

    opened_positions: int
    closed_positions: int
    open_positions: int

    initial_balance: float
    final_cash_balance: float
    final_equity: float

    realized_pnl: float
    unrealized_pnl: float

    total_return_percent: float

    symbols: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReplayRunnerResult:
    status: ReplayRunnerStatus
    statistics: ReplayRunnerStatistics
    signals: tuple[ReplaySignalRecord, ...]


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

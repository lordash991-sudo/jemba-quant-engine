from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TradeAction(StrEnum):
    HOLD = "hold"
    CLOSE = "close"
    BREAK_EVEN = "break_even"
    TRAIL = "trail"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class TradeDecision:
    action: TradeAction
    reason: str | None = None


class TradeManager:
    """
    Coordinate trade-management decisions by priority.

    Priority:
        1. ATR stop
        2. Time stop
        3. Partial take profit
        4. Break even
        5. Trailing stop
        6. Hold
    """

    def decide(
        self,
        *,
        atr_stop: bool = False,
        break_even: bool = False,
        partial_tp: bool = False,
        trailing: bool = False,
        time_stop: bool = False,
    ) -> TradeDecision:
        if atr_stop:
            return TradeDecision(
                action=TradeAction.CLOSE,
                reason="ATR_STOP",
            )

        if time_stop:
            return TradeDecision(
                action=TradeAction.CLOSE,
                reason="TIME_STOP",
            )

        if partial_tp:
            return TradeDecision(
                action=TradeAction.PARTIAL,
                reason="PARTIAL_TP",
            )

        if break_even:
            return TradeDecision(
                action=TradeAction.BREAK_EVEN,
                reason="BREAK_EVEN",
            )

        if trailing:
            return TradeDecision(
                action=TradeAction.TRAIL,
                reason="TRAILING",
            )

        return TradeDecision(
            action=TradeAction.HOLD,
        )

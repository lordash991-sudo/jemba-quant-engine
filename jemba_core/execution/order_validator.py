from __future__ import annotations

import math
from dataclasses import dataclass

from jemba_core.execution.execution_request import (
    ExecutionRequest,
    OrderSide,
)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    approved: bool
    reasons: tuple[str, ...]

    @property
    def primary_reason(self) -> str | None:
        return self.reasons[0] if self.reasons else None


class OrderValidator:
    def __init__(
        self,
        *,
        maximum_leverage: int = 70,
        maximum_risk_percent: float = 3.0,
        minimum_risk_reward: float = 1.0,
    ) -> None:
        if not isinstance(maximum_leverage, int):
            raise TypeError("MAXIMUM_LEVERAGE_MUST_BE_INTEGER")

        if maximum_leverage <= 0:
            raise ValueError("MAXIMUM_LEVERAGE_MUST_BE_POSITIVE")

        if not math.isfinite(maximum_risk_percent):
            raise ValueError("MAXIMUM_RISK_PERCENT_MUST_BE_FINITE")

        if maximum_risk_percent <= 0.0:
            raise ValueError("MAXIMUM_RISK_PERCENT_MUST_BE_POSITIVE")

        if not math.isfinite(minimum_risk_reward):
            raise ValueError("MINIMUM_RISK_REWARD_MUST_BE_FINITE")

        if minimum_risk_reward <= 0.0:
            raise ValueError("MINIMUM_RISK_REWARD_MUST_BE_POSITIVE")

        self.maximum_leverage = maximum_leverage
        self.maximum_risk_percent = float(maximum_risk_percent)
        self.minimum_risk_reward = float(minimum_risk_reward)

    def validate(
        self,
        request: ExecutionRequest,
    ) -> ValidationResult:
        if not isinstance(request, ExecutionRequest):
            raise TypeError("REQUEST_MUST_BE_EXECUTION_REQUEST")

        reasons: list[str] = []

        symbol = request.symbol.strip()

        if not symbol:
            reasons.append("INVALID_SYMBOL")

        if not request.decision_approved:
            reasons.append("DECISION_REJECTED")

        if not request.market_open:
            reasons.append("MARKET_CLOSED")

        if request.kill_switch:
            reasons.append("KILL_SWITCH_ACTIVE")

        if request.duplicate_position:
            reasons.append("DUPLICATE_POSITION")

        if not request.portfolio_approved:
            reasons.append("PORTFOLIO_REJECTED")

        if not request.exposure_approved:
            reasons.append("EXPOSURE_REJECTED")

        if not request.correlation_approved:
            reasons.append("CORRELATION_REJECTED")

        if not _is_positive_finite(request.entry_price):
            reasons.append("INVALID_ENTRY_PRICE")

        if not _is_positive_finite(request.quantity):
            reasons.append("INVALID_QUANTITY")

        if not _is_positive_finite(request.stop_loss):
            reasons.append("INVALID_STOP_LOSS")

        if not _is_positive_finite(request.take_profit):
            reasons.append("INVALID_TAKE_PROFIT")

        if not isinstance(request.leverage, int):
            reasons.append("INVALID_LEVERAGE")
        elif request.leverage <= 0 or request.leverage > self.maximum_leverage:
            reasons.append("INVALID_LEVERAGE")

        if (
            not math.isfinite(request.risk_percent)
            or request.risk_percent <= 0.0
            or request.risk_percent > self.maximum_risk_percent
        ):
            reasons.append("INVALID_RISK_PERCENT")

        if (
            not math.isfinite(request.available_margin)
            or request.available_margin <= 0.0
        ):
            reasons.append("INVALID_AVAILABLE_MARGIN")

        if (
            _is_positive_finite(request.entry_price)
            and _is_positive_finite(request.stop_loss)
            and _is_positive_finite(request.take_profit)
        ):
            reasons.extend(self._validate_price_structure(request))

        if (
            _is_positive_finite(request.entry_price)
            and _is_positive_finite(request.quantity)
            and isinstance(request.leverage, int)
            and request.leverage > 0
            and math.isfinite(request.available_margin)
        ):
            required_margin = request.entry_price * request.quantity / request.leverage

            if required_margin > request.available_margin:
                reasons.append("INSUFFICIENT_MARGIN")

        return ValidationResult(
            approved=not reasons,
            reasons=tuple(reasons),
        )

    def _validate_price_structure(
        self,
        request: ExecutionRequest,
    ) -> list[str]:
        reasons: list[str] = []

        if request.side is OrderSide.BUY:
            if request.stop_loss >= request.entry_price:
                reasons.append("INVALID_STOP_LOSS")

            if request.take_profit <= request.entry_price:
                reasons.append("INVALID_TAKE_PROFIT")

            risk_distance = request.entry_price - request.stop_loss
            reward_distance = request.take_profit - request.entry_price

        elif request.side is OrderSide.SELL:
            if request.stop_loss <= request.entry_price:
                reasons.append("INVALID_STOP_LOSS")

            if request.take_profit >= request.entry_price:
                reasons.append("INVALID_TAKE_PROFIT")

            risk_distance = request.stop_loss - request.entry_price
            reward_distance = request.entry_price - request.take_profit

        else:
            return ["INVALID_SIDE"]

        if risk_distance > 0.0:
            risk_reward = reward_distance / risk_distance

            if risk_reward < self.minimum_risk_reward:
                reasons.append("RISK_REWARD_TOO_LOW")

        return reasons


def _is_positive_finite(value: float) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(numeric) and numeric > 0.0

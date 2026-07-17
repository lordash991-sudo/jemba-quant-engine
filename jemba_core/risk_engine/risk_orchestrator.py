from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class RiskAction(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    KILL_SWITCH = "kill_switch"


@dataclass(frozen=True, slots=True)
class RiskDecision:
    action: RiskAction
    reason: str | None = None

    @property
    def allowed(self) -> bool:
        return self.action is RiskAction.ALLOW


@dataclass(frozen=True, slots=True)
class RiskLimits:
    max_risk_per_trade: float = 0.01
    max_daily_loss: float = 0.03
    max_drawdown: float = 0.10
    max_open_positions: int = 5
    max_total_exposure: float = 1.00
    max_probability_of_ruin: float = 0.05

    def __post_init__(self) -> None:
        _validate_fraction(
            self.max_risk_per_trade,
            "MAX_RISK_PER_TRADE",
            allow_zero=False,
        )
        _validate_fraction(
            self.max_daily_loss,
            "MAX_DAILY_LOSS",
            allow_zero=False,
        )
        _validate_fraction(
            self.max_drawdown,
            "MAX_DRAWDOWN",
            allow_zero=False,
        )
        _validate_fraction(
            self.max_total_exposure,
            "MAX_TOTAL_EXPOSURE",
            allow_zero=False,
        )
        _validate_fraction(
            self.max_probability_of_ruin,
            "MAX_PROBABILITY_OF_RUIN",
            allow_zero=True,
        )

        if not isinstance(self.max_open_positions, int):
            raise TypeError("MAX_OPEN_POSITIONS_MUST_BE_INTEGER")

        if self.max_open_positions <= 0:
            raise ValueError("MAX_OPEN_POSITIONS_MUST_BE_POSITIVE")


class RiskManager:
    """Evaluate whether a new trade may be opened."""

    def __init__(
        self,
        limits: RiskLimits | None = None,
    ) -> None:
        self.limits = limits or RiskLimits()

    def evaluate(
        self,
        *,
        risk_fraction: float,
        daily_loss_fraction: float,
        drawdown_fraction: float,
        open_positions: int,
        total_exposure_fraction: float,
        probability_of_ruin: float,
        kill_switch: bool = False,
    ) -> RiskDecision:
        self._validate_inputs(
            risk_fraction=risk_fraction,
            daily_loss_fraction=daily_loss_fraction,
            drawdown_fraction=drawdown_fraction,
            open_positions=open_positions,
            total_exposure_fraction=total_exposure_fraction,
            probability_of_ruin=probability_of_ruin,
        )

        if kill_switch:
            return RiskDecision(
                action=RiskAction.KILL_SWITCH,
                reason="KILL_SWITCH_ACTIVE",
            )

        if daily_loss_fraction >= self.limits.max_daily_loss:
            return RiskDecision(
                action=RiskAction.BLOCK,
                reason="DAILY_LOSS_LIMIT",
            )

        if drawdown_fraction >= self.limits.max_drawdown:
            return RiskDecision(
                action=RiskAction.BLOCK,
                reason="MAX_DRAWDOWN_LIMIT",
            )

        if probability_of_ruin > self.limits.max_probability_of_ruin:
            return RiskDecision(
                action=RiskAction.BLOCK,
                reason="PROBABILITY_OF_RUIN_LIMIT",
            )

        if open_positions >= self.limits.max_open_positions:
            return RiskDecision(
                action=RiskAction.BLOCK,
                reason="MAX_OPEN_POSITIONS",
            )

        if total_exposure_fraction >= self.limits.max_total_exposure:
            return RiskDecision(
                action=RiskAction.BLOCK,
                reason="TOTAL_EXPOSURE_LIMIT",
            )

        if risk_fraction > self.limits.max_risk_per_trade:
            return RiskDecision(
                action=RiskAction.BLOCK,
                reason="RISK_PER_TRADE_LIMIT",
            )

        return RiskDecision(
            action=RiskAction.ALLOW,
        )

    @staticmethod
    def _validate_inputs(
        *,
        risk_fraction: float,
        daily_loss_fraction: float,
        drawdown_fraction: float,
        open_positions: int,
        total_exposure_fraction: float,
        probability_of_ruin: float,
    ) -> None:
        _validate_fraction(
            risk_fraction,
            "RISK_FRACTION",
            allow_zero=True,
        )
        _validate_fraction(
            daily_loss_fraction,
            "DAILY_LOSS_FRACTION",
            allow_zero=True,
        )
        _validate_fraction(
            drawdown_fraction,
            "DRAWDOWN_FRACTION",
            allow_zero=True,
        )
        _validate_fraction(
            total_exposure_fraction,
            "TOTAL_EXPOSURE_FRACTION",
            allow_zero=True,
        )
        _validate_fraction(
            probability_of_ruin,
            "PROBABILITY_OF_RUIN",
            allow_zero=True,
        )

        if not isinstance(open_positions, int):
            raise TypeError("OPEN_POSITIONS_MUST_BE_INTEGER")

        if open_positions < 0:
            raise ValueError("OPEN_POSITIONS_MUST_BE_NON_NEGATIVE")


def _validate_fraction(
    value: float,
    name: str,
    *,
    allow_zero: bool,
) -> None:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name}_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name}_MUST_BE_FINITE")

    minimum_valid = numeric >= 0.0 if allow_zero else numeric > 0.0

    if not minimum_valid or numeric > 1.0:
        suffix = (
            "MUST_BE_BETWEEN_0_AND_1"
            if allow_zero
            else "MUST_BE_BETWEEN_0_EXCLUSIVE_AND_1"
        )
        raise ValueError(f"{name}_{suffix}")

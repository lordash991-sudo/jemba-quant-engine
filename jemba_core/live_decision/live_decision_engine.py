from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum


class DecisionSide(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class DecisionStatus(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class LiveDecisionInput:
    """Precomputed inputs required to approve or reject a trade."""

    symbol: str
    side: DecisionSide

    ai_confidence: float
    monte_carlo_confidence: float
    strategy_confidence: float
    edge_score: float

    risk_approved: bool
    portfolio_approved: bool
    exposure_approved: bool
    correlation_approved: bool

    risk_percent: float
    position_fraction: float
    leverage: int

    probability_of_ruin: float = 0.0
    max_drawdown: float = 0.0
    kill_switch: bool = False


@dataclass(frozen=True, slots=True)
class LiveDecisionLimits:
    """Thresholds used by the Live Decision Engine."""

    minimum_ai_confidence: float = 70.0
    minimum_monte_carlo_confidence: float = 70.0
    minimum_strategy_confidence: float = 70.0
    minimum_edge_score: float = 65.0

    maximum_probability_of_ruin: float = 0.05
    maximum_drawdown: float = 0.20

    maximum_risk_percent: float = 3.0
    maximum_position_fraction: float = 0.30
    maximum_leverage: int = 70

    def __post_init__(self) -> None:
        _validate_score(
            self.minimum_ai_confidence,
            "MINIMUM_AI_CONFIDENCE",
        )
        _validate_score(
            self.minimum_monte_carlo_confidence,
            "MINIMUM_MONTE_CARLO_CONFIDENCE",
        )
        _validate_score(
            self.minimum_strategy_confidence,
            "MINIMUM_STRATEGY_CONFIDENCE",
        )
        _validate_score(
            self.minimum_edge_score,
            "MINIMUM_EDGE_SCORE",
        )

        _validate_fraction(
            self.maximum_probability_of_ruin,
            "MAXIMUM_PROBABILITY_OF_RUIN",
        )
        _validate_fraction(
            self.maximum_drawdown,
            "MAXIMUM_DRAWDOWN",
        )

        _validate_non_negative(
            self.maximum_risk_percent,
            "MAXIMUM_RISK_PERCENT",
        )
        _validate_fraction(
            self.maximum_position_fraction,
            "MAXIMUM_POSITION_FRACTION",
        )

        if not isinstance(self.maximum_leverage, int):
            raise TypeError("MAXIMUM_LEVERAGE_MUST_BE_INTEGER")

        if self.maximum_leverage <= 0:
            raise ValueError("MAXIMUM_LEVERAGE_MUST_BE_POSITIVE")


@dataclass(frozen=True, slots=True)
class LiveDecision:
    """Final trade decision emitted before execution."""

    status: DecisionStatus
    approved: bool

    symbol: str
    side: DecisionSide

    confidence: float
    edge_score: float

    risk_percent: float
    position_fraction: float
    leverage: int

    reasons: tuple[str, ...]

    @property
    def primary_reason(self) -> str | None:
        return self.reasons[0] if self.reasons else None


class LiveDecisionEngine:
    """
    Produce the final approval or rejection before order execution.

    This engine consumes results already calculated by the other
    JEMBA components. It does not retrain models or calculate indicators.
    """

    def __init__(
        self,
        limits: LiveDecisionLimits | None = None,
    ) -> None:
        self.limits = limits or LiveDecisionLimits()

    def decide(
        self,
        decision_input: LiveDecisionInput,
    ) -> LiveDecision:
        validated = _validate_input(decision_input)

        rejection_reasons = self._rejection_reasons(validated)

        confidence = self.calculate_combined_confidence(
            ai_confidence=validated.ai_confidence,
            monte_carlo_confidence=(validated.monte_carlo_confidence),
            strategy_confidence=validated.strategy_confidence,
            edge_score=validated.edge_score,
        )

        if rejection_reasons:
            return LiveDecision(
                status=DecisionStatus.REJECTED,
                approved=False,
                symbol=validated.symbol,
                side=validated.side,
                confidence=confidence,
                edge_score=validated.edge_score,
                risk_percent=0.0,
                position_fraction=0.0,
                leverage=0,
                reasons=tuple(rejection_reasons),
            )

        approval_reasons = (
            "AI_CONFIDENCE_OK",
            "MONTE_CARLO_CONFIDENCE_OK",
            "STRATEGY_CONFIDENCE_OK",
            "EDGE_SCORE_OK",
            "RISK_APPROVED",
            "PORTFOLIO_APPROVED",
            "EXPOSURE_APPROVED",
            "CORRELATION_APPROVED",
            "PROBABILITY_OF_RUIN_OK",
            "DRAWDOWN_OK",
        )

        return LiveDecision(
            status=DecisionStatus.APPROVED,
            approved=True,
            symbol=validated.symbol,
            side=validated.side,
            confidence=confidence,
            edge_score=validated.edge_score,
            risk_percent=validated.risk_percent,
            position_fraction=validated.position_fraction,
            leverage=min(
                validated.leverage,
                self.limits.maximum_leverage,
            ),
            reasons=approval_reasons,
        )

    @staticmethod
    def calculate_combined_confidence(
        *,
        ai_confidence: float,
        monte_carlo_confidence: float,
        strategy_confidence: float,
        edge_score: float,
    ) -> float:
        ai = _validate_score(
            ai_confidence,
            "AI_CONFIDENCE",
        )
        monte_carlo = _validate_score(
            monte_carlo_confidence,
            "MONTE_CARLO_CONFIDENCE",
        )
        strategy = _validate_score(
            strategy_confidence,
            "STRATEGY_CONFIDENCE",
        )
        edge = _validate_score(
            edge_score,
            "EDGE_SCORE",
        )

        result = ai * 0.35 + monte_carlo * 0.25 + strategy * 0.25 + edge * 0.15

        return round(result, 4)

    def decide_many(
        self,
        inputs: Sequence[LiveDecisionInput],
    ) -> tuple[LiveDecision, ...]:
        if isinstance(inputs, (str, bytes)):
            raise TypeError("DECISION_INPUTS_MUST_BE_SEQUENCE")

        try:
            values = tuple(inputs)
        except TypeError as exc:
            raise TypeError("DECISION_INPUTS_MUST_BE_SEQUENCE") from exc

        if not values:
            raise ValueError("DECISION_INPUTS_CANNOT_BE_EMPTY")

        return tuple(self.decide(value) for value in values)

    def _rejection_reasons(
        self,
        decision_input: LiveDecisionInput,
    ) -> list[str]:
        reasons: list[str] = []

        if decision_input.kill_switch:
            reasons.append("KILL_SWITCH_ACTIVE")

        if decision_input.ai_confidence < self.limits.minimum_ai_confidence:
            reasons.append("AI_CONFIDENCE_TOO_LOW")

        if (
            decision_input.monte_carlo_confidence
            < self.limits.minimum_monte_carlo_confidence
        ):
            reasons.append("MONTE_CARLO_CONFIDENCE_TOO_LOW")

        if decision_input.strategy_confidence < self.limits.minimum_strategy_confidence:
            reasons.append("STRATEGY_CONFIDENCE_TOO_LOW")

        if decision_input.edge_score < self.limits.minimum_edge_score:
            reasons.append("EDGE_SCORE_TOO_LOW")

        if not decision_input.risk_approved:
            reasons.append("RISK_REJECTED")

        if not decision_input.portfolio_approved:
            reasons.append("PORTFOLIO_REJECTED")

        if not decision_input.exposure_approved:
            reasons.append("EXPOSURE_REJECTED")

        if not decision_input.correlation_approved:
            reasons.append("CORRELATION_REJECTED")

        if decision_input.probability_of_ruin > self.limits.maximum_probability_of_ruin:
            reasons.append("PROBABILITY_OF_RUIN_TOO_HIGH")

        if decision_input.max_drawdown > self.limits.maximum_drawdown:
            reasons.append("DRAWDOWN_TOO_HIGH")

        if decision_input.risk_percent > self.limits.maximum_risk_percent:
            reasons.append("RISK_PERCENT_TOO_HIGH")

        if decision_input.position_fraction > self.limits.maximum_position_fraction:
            reasons.append("POSITION_FRACTION_TOO_HIGH")

        if decision_input.leverage > self.limits.maximum_leverage:
            reasons.append("LEVERAGE_TOO_HIGH")

        return reasons


def _validate_input(
    value: LiveDecisionInput,
) -> LiveDecisionInput:
    if not isinstance(value, LiveDecisionInput):
        raise TypeError("DECISION_INPUT_MUST_BE_LIVE_DECISION_INPUT")

    symbol = value.symbol.strip()

    if not symbol:
        raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

    if not isinstance(value.side, DecisionSide):
        raise TypeError("SIDE_MUST_BE_DECISION_SIDE")

    _validate_score(
        value.ai_confidence,
        "AI_CONFIDENCE",
    )
    _validate_score(
        value.monte_carlo_confidence,
        "MONTE_CARLO_CONFIDENCE",
    )
    _validate_score(
        value.strategy_confidence,
        "STRATEGY_CONFIDENCE",
    )
    _validate_score(
        value.edge_score,
        "EDGE_SCORE",
    )

    for field_name, field_value in (
        ("RISK_APPROVED", value.risk_approved),
        ("PORTFOLIO_APPROVED", value.portfolio_approved),
        ("EXPOSURE_APPROVED", value.exposure_approved),
        ("CORRELATION_APPROVED", value.correlation_approved),
        ("KILL_SWITCH", value.kill_switch),
    ):
        if not isinstance(field_value, bool):
            raise TypeError(f"{field_name}_MUST_BE_BOOLEAN")

    _validate_non_negative(
        value.risk_percent,
        "RISK_PERCENT",
    )
    _validate_fraction(
        value.position_fraction,
        "POSITION_FRACTION",
    )
    _validate_fraction(
        value.probability_of_ruin,
        "PROBABILITY_OF_RUIN",
    )
    _validate_fraction(
        value.max_drawdown,
        "MAX_DRAWDOWN",
    )

    if not isinstance(value.leverage, int):
        raise TypeError("LEVERAGE_MUST_BE_INTEGER")

    if value.leverage < 0:
        raise ValueError("LEVERAGE_MUST_BE_NON_NEGATIVE")

    return LiveDecisionInput(
        symbol=symbol.upper(),
        side=value.side,
        ai_confidence=float(value.ai_confidence),
        monte_carlo_confidence=float(value.monte_carlo_confidence),
        strategy_confidence=float(value.strategy_confidence),
        edge_score=float(value.edge_score),
        risk_approved=value.risk_approved,
        portfolio_approved=value.portfolio_approved,
        exposure_approved=value.exposure_approved,
        correlation_approved=value.correlation_approved,
        risk_percent=float(value.risk_percent),
        position_fraction=float(value.position_fraction),
        leverage=value.leverage,
        probability_of_ruin=float(value.probability_of_ruin),
        max_drawdown=float(value.max_drawdown),
        kill_switch=value.kill_switch,
    )


def _validate_score(
    value: float,
    name: str,
) -> float:
    numeric = _to_finite_float(value, name)

    if not 0.0 <= numeric <= 100.0:
        raise ValueError(f"{name}_MUST_BE_BETWEEN_0_AND_100")

    return numeric


def _validate_fraction(
    value: float,
    name: str,
) -> float:
    numeric = _to_finite_float(value, name)

    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name}_MUST_BE_BETWEEN_0_AND_1")

    return numeric


def _validate_non_negative(
    value: float,
    name: str,
) -> float:
    numeric = _to_finite_float(value, name)

    if numeric < 0.0:
        raise ValueError(f"{name}_MUST_BE_NON_NEGATIVE")

    return numeric


def _to_finite_float(
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

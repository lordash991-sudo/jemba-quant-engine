from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import fmean, stdev


@dataclass(frozen=True, slots=True)
class StrategyMetrics:
    trade_count: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    expectancy: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    sqn: float
    kelly_fraction: float
    total_return: float
    max_drawdown: float


@dataclass(frozen=True, slots=True)
class StrategyEvaluation:
    metrics: StrategyMetrics
    edge_score: float
    confidence_score: float
    approved: bool
    leverage: int
    reason: str | None = None


class StrategyEvaluator:
    """Evaluate strategy quality from decimal trade returns."""

    def __init__(
        self,
        *,
        minimum_trades: int = 20,
        minimum_confidence: float = 70.0,
        annualization_factor: int = 252,
    ) -> None:
        if not isinstance(minimum_trades, int):
            raise TypeError("MINIMUM_TRADES_MUST_BE_INTEGER")

        if minimum_trades <= 0:
            raise ValueError("MINIMUM_TRADES_MUST_BE_POSITIVE")

        if not math.isfinite(minimum_confidence):
            raise ValueError("MINIMUM_CONFIDENCE_MUST_BE_FINITE")

        if not 0.0 <= minimum_confidence <= 100.0:
            raise ValueError("MINIMUM_CONFIDENCE_MUST_BE_BETWEEN_0_AND_100")

        if not isinstance(annualization_factor, int):
            raise TypeError("ANNUALIZATION_FACTOR_MUST_BE_INTEGER")

        if annualization_factor <= 0:
            raise ValueError("ANNUALIZATION_FACTOR_MUST_BE_POSITIVE")

        self.minimum_trades = minimum_trades
        self.minimum_confidence = float(minimum_confidence)
        self.annualization_factor = annualization_factor

    def evaluate(
        self,
        trade_returns: Sequence[float],
        *,
        ai_confidence: float = 0.0,
        monte_carlo_confidence: float = 0.0,
        risk_score: float = 100.0,
        correlation_score: float = 100.0,
    ) -> StrategyEvaluation:
        returns = _validate_returns(trade_returns)

        ai_confidence = _validate_score(
            ai_confidence,
            "AI_CONFIDENCE",
        )
        monte_carlo_confidence = _validate_score(
            monte_carlo_confidence,
            "MONTE_CARLO_CONFIDENCE",
        )
        risk_score = _validate_score(
            risk_score,
            "RISK_SCORE",
        )
        correlation_score = _validate_score(
            correlation_score,
            "CORRELATION_SCORE",
        )

        metrics = self.calculate_metrics(returns)
        edge_score = self.calculate_edge_score(metrics)

        confidence_score = self.calculate_confidence_score(
            edge_score=edge_score,
            ai_confidence=ai_confidence,
            monte_carlo_confidence=monte_carlo_confidence,
            risk_score=risk_score,
            correlation_score=correlation_score,
        )

        reason = self._rejection_reason(
            metrics=metrics,
            confidence_score=confidence_score,
        )

        approved = reason is None

        return StrategyEvaluation(
            metrics=metrics,
            edge_score=edge_score,
            confidence_score=confidence_score,
            approved=approved,
            leverage=(
                self.leverage_for_confidence(confidence_score) if approved else 0
            ),
            reason=reason,
        )

    def calculate_metrics(
        self,
        trade_returns: Sequence[float],
    ) -> StrategyMetrics:
        returns = _validate_returns(trade_returns)

        wins = tuple(value for value in returns if value > 0.0)
        losses = tuple(value for value in returns if value < 0.0)

        trade_count = len(returns)
        win_rate = len(wins) / trade_count

        average_win = fmean(wins) if wins else 0.0
        average_loss = fmean(losses) if losses else 0.0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))

        if gross_loss == 0.0:
            profit_factor = math.inf if gross_profit > 0.0 else 0.0
        else:
            profit_factor = gross_profit / gross_loss

        expectancy = fmean(returns)
        total_return = math.prod(1.0 + value for value in returns) - 1.0

        standard_deviation = stdev(returns) if trade_count > 1 else 0.0

        sharpe_ratio = (
            expectancy / standard_deviation * math.sqrt(self.annualization_factor)
            if standard_deviation > 0.0
            else 0.0
        )

        downside_returns = tuple(value for value in returns if value < 0.0)

        downside_deviation = (
            math.sqrt(fmean(value**2 for value in downside_returns))
            if downside_returns
            else 0.0
        )

        sortino_ratio = (
            expectancy / downside_deviation * math.sqrt(self.annualization_factor)
            if downside_deviation > 0.0
            else 0.0
        )

        max_drawdown = _calculate_max_drawdown(returns)

        calmar_ratio = total_return / max_drawdown if max_drawdown > 0.0 else 0.0

        sqn = (
            math.sqrt(trade_count) * expectancy / standard_deviation
            if standard_deviation > 0.0
            else 0.0
        )

        payoff_ratio = average_win / abs(average_loss) if average_loss < 0.0 else 0.0

        kelly_fraction = (
            win_rate - ((1.0 - win_rate) / payoff_ratio) if payoff_ratio > 0.0 else 0.0
        )

        kelly_fraction = _clamp(
            kelly_fraction,
            0.0,
            1.0,
        )

        return StrategyMetrics(
            trade_count=trade_count,
            win_rate=float(win_rate),
            average_win=float(average_win),
            average_loss=float(average_loss),
            profit_factor=float(profit_factor),
            expectancy=float(expectancy),
            sharpe_ratio=float(sharpe_ratio),
            sortino_ratio=float(sortino_ratio),
            calmar_ratio=float(calmar_ratio),
            sqn=float(sqn),
            kelly_fraction=float(kelly_fraction),
            total_return=float(total_return),
            max_drawdown=float(max_drawdown),
        )

    @staticmethod
    def calculate_edge_score(
        metrics: StrategyMetrics,
    ) -> float:
        win_rate_score = _normalize(
            metrics.win_rate,
            0.35,
            0.70,
        )

        profit_factor_value = (
            3.0 if math.isinf(metrics.profit_factor) else metrics.profit_factor
        )

        profit_factor_score = _normalize(
            profit_factor_value,
            1.0,
            3.0,
        )

        expectancy_score = _normalize(
            metrics.expectancy,
            0.0,
            0.03,
        )

        drawdown_score = 100.0 - _normalize(
            metrics.max_drawdown,
            0.05,
            0.40,
        )

        sqn_score = _normalize(
            metrics.sqn,
            0.0,
            4.0,
        )

        kelly_score = _normalize(
            metrics.kelly_fraction,
            0.0,
            0.30,
        )

        score = (
            win_rate_score * 0.30
            + profit_factor_score * 0.25
            + expectancy_score * 0.15
            + drawdown_score * 0.15
            + sqn_score * 0.10
            + kelly_score * 0.05
        )

        return round(_clamp(score, 0.0, 100.0), 4)

    @staticmethod
    def calculate_confidence_score(
        *,
        edge_score: float,
        ai_confidence: float,
        monte_carlo_confidence: float,
        risk_score: float,
        correlation_score: float,
    ) -> float:
        scores = (
            _validate_score(edge_score, "EDGE_SCORE"),
            _validate_score(ai_confidence, "AI_CONFIDENCE"),
            _validate_score(
                monte_carlo_confidence,
                "MONTE_CARLO_CONFIDENCE",
            ),
            _validate_score(risk_score, "RISK_SCORE"),
            _validate_score(
                correlation_score,
                "CORRELATION_SCORE",
            ),
        )

        confidence = (
            scores[0] * 0.35
            + scores[1] * 0.25
            + scores[2] * 0.20
            + scores[3] * 0.15
            + scores[4] * 0.05
        )

        return round(
            _clamp(confidence, 0.0, 100.0),
            4,
        )

    @staticmethod
    def leverage_for_confidence(
        confidence_score: float,
    ) -> int:
        confidence_score = _validate_score(
            confidence_score,
            "CONFIDENCE_SCORE",
        )

        if confidence_score >= 95.0:
            return 70

        if confidence_score >= 90.0:
            return 50

        if confidence_score >= 85.0:
            return 35

        if confidence_score >= 80.0:
            return 20

        if confidence_score >= 70.0:
            return 10

        return 0

    def _rejection_reason(
        self,
        *,
        metrics: StrategyMetrics,
        confidence_score: float,
    ) -> str | None:
        if metrics.trade_count < self.minimum_trades:
            return "INSUFFICIENT_TRADES"

        if metrics.expectancy <= 0.0:
            return "NEGATIVE_EXPECTANCY"

        if metrics.profit_factor <= 1.0:
            return "PROFIT_FACTOR_TOO_LOW"

        if confidence_score < self.minimum_confidence:
            return "CONFIDENCE_TOO_LOW"

        return None


def _validate_returns(
    trade_returns: Sequence[float],
) -> tuple[float, ...]:
    if isinstance(trade_returns, (str, bytes)):
        raise TypeError("TRADE_RETURNS_MUST_BE_NUMERIC_SEQUENCE")

    try:
        returns = tuple(float(value) for value in trade_returns)
    except (TypeError, ValueError) as exc:
        raise TypeError("TRADE_RETURNS_MUST_BE_NUMERIC_SEQUENCE") from exc

    if not returns:
        raise ValueError("TRADE_RETURNS_CANNOT_BE_EMPTY")

    for value in returns:
        if not math.isfinite(value):
            raise ValueError("TRADE_RETURN_MUST_BE_FINITE")

        if value <= -1.0:
            raise ValueError("TRADE_RETURN_MUST_BE_GREATER_THAN_MINUS_ONE")

    return returns


def _validate_score(
    score: float,
    name: str,
) -> float:
    try:
        numeric = float(score)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name}_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name}_MUST_BE_FINITE")

    if not 0.0 <= numeric <= 100.0:
        raise ValueError(f"{name}_MUST_BE_BETWEEN_0_AND_100")

    return numeric


def _calculate_max_drawdown(
    trade_returns: Sequence[float],
) -> float:
    equity = 1.0
    peak = equity
    max_drawdown = 0.0

    for trade_return in trade_returns:
        equity *= 1.0 + trade_return
        peak = max(peak, equity)

        drawdown = (peak - equity) / peak
        max_drawdown = max(max_drawdown, drawdown)

    return float(max_drawdown)


def _normalize(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    if maximum <= minimum:
        raise ValueError("NORMALIZATION_MAXIMUM_MUST_EXCEED_MINIMUM")

    normalized = (value - minimum) / (maximum - minimum) * 100.0

    return _clamp(normalized, 0.0, 100.0)


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(minimum, min(maximum, value))

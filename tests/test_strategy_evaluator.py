import math

import pytest

from jemba_core.strategy.strategy_evaluator import (
    StrategyEvaluation,
    StrategyEvaluator,
)

PROFITABLE_RETURNS = [
    0.03,
    0.02,
    -0.01,
    0.025,
    -0.015,
    0.04,
    0.01,
    -0.01,
    0.03,
    0.02,
] * 3


def test_calculates_strategy_metrics():
    evaluator = StrategyEvaluator()

    metrics = evaluator.calculate_metrics(PROFITABLE_RETURNS)

    assert metrics.trade_count == 30
    assert 0.0 < metrics.win_rate < 1.0
    assert metrics.average_win > 0.0
    assert metrics.average_loss < 0.0
    assert metrics.profit_factor > 1.0
    assert metrics.expectancy > 0.0
    assert metrics.total_return > 0.0
    assert metrics.max_drawdown > 0.0


def test_evaluates_profitable_strategy():
    evaluator = StrategyEvaluator(minimum_confidence=60.0)

    result = evaluator.evaluate(
        PROFITABLE_RETURNS,
        ai_confidence=90.0,
        monte_carlo_confidence=88.0,
        risk_score=95.0,
        correlation_score=90.0,
    )

    assert isinstance(result, StrategyEvaluation)
    assert result.approved is True
    assert result.reason is None
    assert result.edge_score > 0.0
    assert result.confidence_score >= 60.0
    assert result.leverage > 0


def test_rejects_insufficient_trades():
    evaluator = StrategyEvaluator(minimum_trades=20)

    result = evaluator.evaluate(
        [0.02, -0.01, 0.03],
        ai_confidence=100.0,
        monte_carlo_confidence=100.0,
    )

    assert result.approved is False
    assert result.reason == "INSUFFICIENT_TRADES"
    assert result.leverage == 0


def test_rejects_negative_expectancy():
    evaluator = StrategyEvaluator(minimum_trades=4)

    result = evaluator.evaluate(
        [-0.03, -0.02, 0.01, -0.01],
        ai_confidence=100.0,
        monte_carlo_confidence=100.0,
    )

    assert result.approved is False
    assert result.reason == "NEGATIVE_EXPECTANCY"


def test_rejects_low_confidence():
    evaluator = StrategyEvaluator(minimum_confidence=90.0)

    result = evaluator.evaluate(
        PROFITABLE_RETURNS,
        ai_confidence=50.0,
        monte_carlo_confidence=50.0,
        risk_score=50.0,
        correlation_score=50.0,
    )

    assert result.approved is False
    assert result.reason == "CONFIDENCE_TOO_LOW"


@pytest.mark.parametrize(
    ("confidence", "expected_leverage"),
    [
        (96.0, 70),
        (92.0, 50),
        (87.0, 35),
        (82.0, 20),
        (72.0, 10),
        (69.0, 0),
    ],
)
def test_leverage_mapping(
    confidence,
    expected_leverage,
):
    assert StrategyEvaluator.leverage_for_confidence(confidence) == expected_leverage


def test_profit_factor_is_infinite_without_losses():
    evaluator = StrategyEvaluator(minimum_trades=3)

    metrics = evaluator.calculate_metrics([0.01, 0.02, 0.03])

    assert math.isinf(metrics.profit_factor)


def test_kelly_is_bounded():
    evaluator = StrategyEvaluator()

    metrics = evaluator.calculate_metrics(PROFITABLE_RETURNS)

    assert 0.0 <= metrics.kelly_fraction <= 1.0


def test_rejects_empty_returns():
    evaluator = StrategyEvaluator()

    with pytest.raises(
        ValueError,
        match="TRADE_RETURNS_CANNOT_BE_EMPTY",
    ):
        evaluator.evaluate([])


def test_rejects_invalid_return():
    evaluator = StrategyEvaluator()

    with pytest.raises(
        ValueError,
        match="TRADE_RETURN_MUST_BE_GREATER_THAN_MINUS_ONE",
    ):
        evaluator.evaluate([0.02, -1.0])


def test_rejects_invalid_score():
    evaluator = StrategyEvaluator()

    with pytest.raises(
        ValueError,
        match="AI_CONFIDENCE_MUST_BE_BETWEEN_0_AND_100",
    ):
        evaluator.evaluate(
            PROFITABLE_RETURNS,
            ai_confidence=101.0,
        )

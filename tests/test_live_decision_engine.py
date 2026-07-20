import pytest

from jemba_core.live_decision import (
    DecisionSide,
    DecisionStatus,
    LiveDecisionEngine,
    LiveDecisionInput,
    LiveDecisionLimits,
)


def valid_input(**overrides):
    values = {
        "symbol": "BTCUSDT",
        "side": DecisionSide.LONG,
        "ai_confidence": 92.0,
        "monte_carlo_confidence": 88.0,
        "strategy_confidence": 90.0,
        "edge_score": 86.0,
        "risk_approved": True,
        "portfolio_approved": True,
        "exposure_approved": True,
        "correlation_approved": True,
        "risk_percent": 1.0,
        "position_fraction": 0.15,
        "leverage": 35,
        "probability_of_ruin": 0.02,
        "max_drawdown": 0.10,
        "kill_switch": False,
    }
    values.update(overrides)

    return LiveDecisionInput(**values)


def test_approves_valid_trade():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input())

    assert result.approved is True
    assert result.status is DecisionStatus.APPROVED
    assert result.symbol == "BTCUSDT"
    assert result.side is DecisionSide.LONG
    assert result.leverage == 35
    assert result.risk_percent == pytest.approx(1.0)
    assert result.position_fraction == pytest.approx(0.15)
    assert result.primary_reason == "AI_CONFIDENCE_OK"


def test_normalizes_symbol():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(symbol=" ethusdt "))

    assert result.symbol == "ETHUSDT"


def test_rejects_low_ai_confidence():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(ai_confidence=60.0))

    assert result.approved is False
    assert result.status is DecisionStatus.REJECTED
    assert "AI_CONFIDENCE_TOO_LOW" in result.reasons
    assert result.leverage == 0
    assert result.risk_percent == 0.0


def test_rejects_monte_carlo_confidence():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(monte_carlo_confidence=50.0))

    assert result.approved is False
    assert "MONTE_CARLO_CONFIDENCE_TOO_LOW" in result.reasons


def test_rejects_strategy_confidence():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(strategy_confidence=50.0))

    assert result.approved is False
    assert "STRATEGY_CONFIDENCE_TOO_LOW" in result.reasons


def test_rejects_low_edge():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(edge_score=50.0))

    assert result.approved is False
    assert "EDGE_SCORE_TOO_LOW" in result.reasons


@pytest.mark.parametrize(
    ("field", "reason"),
    [
        ("risk_approved", "RISK_REJECTED"),
        ("portfolio_approved", "PORTFOLIO_REJECTED"),
        ("exposure_approved", "EXPOSURE_REJECTED"),
        (
            "correlation_approved",
            "CORRELATION_REJECTED",
        ),
    ],
)
def test_rejects_component_failure(
    field,
    reason,
):
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(**{field: False}))

    assert result.approved is False
    assert reason in result.reasons


def test_kill_switch_has_priority():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(kill_switch=True))

    assert result.approved is False
    assert result.primary_reason == "KILL_SWITCH_ACTIVE"


def test_rejects_probability_of_ruin():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(probability_of_ruin=0.10))

    assert result.approved is False
    assert "PROBABILITY_OF_RUIN_TOO_HIGH" in result.reasons


def test_rejects_drawdown():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(max_drawdown=0.30))

    assert result.approved is False
    assert "DRAWDOWN_TOO_HIGH" in result.reasons


def test_rejects_excessive_leverage():
    engine = LiveDecisionEngine()

    result = engine.decide(valid_input(leverage=100))

    assert result.approved is False
    assert "LEVERAGE_TOO_HIGH" in result.reasons


def test_custom_limits():
    engine = LiveDecisionEngine(
        LiveDecisionLimits(
            minimum_ai_confidence=80.0,
            minimum_monte_carlo_confidence=80.0,
            minimum_strategy_confidence=80.0,
            minimum_edge_score=80.0,
            maximum_leverage=50,
        )
    )

    result = engine.decide(valid_input())

    assert result.approved is True


def test_combined_confidence():
    result = LiveDecisionEngine.calculate_combined_confidence(
        ai_confidence=100.0,
        monte_carlo_confidence=100.0,
        strategy_confidence=100.0,
        edge_score=100.0,
    )

    assert result == pytest.approx(100.0)


def test_decide_many():
    engine = LiveDecisionEngine()

    results = engine.decide_many(
        [
            valid_input(symbol="BTCUSDT"),
            valid_input(
                symbol="ETHUSDT",
                risk_approved=False,
            ),
        ]
    )

    assert len(results) == 2
    assert results[0].approved is True
    assert results[1].approved is False


def test_rejects_invalid_input_type():
    engine = LiveDecisionEngine()

    with pytest.raises(
        TypeError,
        match="DECISION_INPUT_MUST_BE_LIVE_DECISION_INPUT",
    ):
        engine.decide({})


def test_rejects_empty_symbol():
    engine = LiveDecisionEngine()

    with pytest.raises(
        ValueError,
        match="SYMBOL_CANNOT_BE_EMPTY",
    ):
        engine.decide(valid_input(symbol=" "))


def test_rejects_invalid_score():
    engine = LiveDecisionEngine()

    with pytest.raises(
        ValueError,
        match="AI_CONFIDENCE_MUST_BE_BETWEEN_0_AND_100",
    ):
        engine.decide(valid_input(ai_confidence=101.0))


def test_rejects_empty_collection():
    engine = LiveDecisionEngine()

    with pytest.raises(
        ValueError,
        match="DECISION_INPUTS_CANNOT_BE_EMPTY",
    ):
        engine.decide_many([])

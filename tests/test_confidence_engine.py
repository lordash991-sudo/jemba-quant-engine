from jemba_core.ai.confidence_engine import ConfidenceEngine


def test_confidence_score():

    engine = ConfidenceEngine()

    result = engine.calculate(
        ai_probability=0.92,
        trend_score=0.85,
        volatility_score=0.75,
        momentum_score=0.80,
    )

    assert result.score > 0.80


def test_confidence_clamps_values():

    engine = ConfidenceEngine()

    result = engine.calculate(
        ai_probability=5,
        trend_score=-2,
        volatility_score=0.5,
        momentum_score=2,
    )

    assert result.ai == 1
    assert result.trend == 0
    assert result.momentum == 1
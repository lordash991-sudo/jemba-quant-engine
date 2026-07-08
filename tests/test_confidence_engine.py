from jemba_core.ai.confidence_engine import ConfidenceEngine


def test_low_probability():
    engine = ConfidenceEngine()

    result = engine.calculate(
        prediction=1,
        probability=0.51,
    )

    assert result.confidence == 0


def test_medium_probability():
    engine = ConfidenceEngine()

    result = engine.calculate(
        prediction=1,
        probability=0.70,
    )

    assert result.confidence > 20


def test_high_probability():
    engine = ConfidenceEngine()

    result = engine.calculate(
        prediction=1,
        probability=0.95,
    )

    assert result.confidence > 85


def test_probability_is_preserved():
    engine = ConfidenceEngine()

    result = engine.calculate(
        prediction=0,
        probability=0.81,
    )

    assert result.probability == 0.81


def test_prediction_is_preserved():
    engine = ConfidenceEngine()

    result = engine.calculate(
        prediction=1,
        probability=0.80,
    )

    assert result.prediction == 1

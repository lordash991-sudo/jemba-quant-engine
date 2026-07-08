from jemba_core.ai.confidence_engine import ConfidenceResult
from jemba_core.ai.signal_engine import SignalEngine


def test_buy_signal():

    signal = SignalEngine()

    confidence = ConfidenceResult(
        confidence=90,
        probability=0.95,
        prediction=1,
    )

    result = signal.generate(confidence)

    assert result.action == "BUY"


def test_sell_signal():

    signal = SignalEngine()

    confidence = ConfidenceResult(
        confidence=91,
        probability=0.93,
        prediction=-1,
    )

    result = signal.generate(confidence)

    assert result.action == "SELL"


def test_hold_low_confidence():

    signal = SignalEngine()

    confidence = ConfidenceResult(
        confidence=20,
        probability=0.60,
        prediction=1,
    )

    result = signal.generate(confidence)

    assert result.action == "HOLD"


def test_probability_preserved():

    signal = SignalEngine()

    confidence = ConfidenceResult(
        confidence=80,
        probability=0.87,
        prediction=1,
    )

    result = signal.generate(confidence)

    assert result.probability == 0.87


def test_confidence_preserved():

    signal = SignalEngine()

    confidence = ConfidenceResult(
        confidence=77,
        probability=0.82,
        prediction=-1,
    )

    result = signal.generate(confidence)

    assert result.confidence == 77

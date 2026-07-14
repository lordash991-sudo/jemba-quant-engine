import pytest

from jemba_core.montecarlo import (
    confidence_interval,
    mean,
    median,
    percentile,
    standard_deviation,
)


def test_calculates_basic_statistics():
    values = [1.0, 2.0, 3.0, 4.0]

    assert mean(values) == pytest.approx(2.5)
    assert median(values) == pytest.approx(2.5)
    assert standard_deviation(values) > 0.0
    assert percentile(values, 50.0) == pytest.approx(2.5)


def test_calculates_confidence_interval():
    lower, upper = confidence_interval(
        range(1, 101),
        confidence=0.90,
    )

    assert lower < upper
    assert 1.0 <= lower <= 100.0
    assert 1.0 <= upper <= 100.0


def test_rejects_invalid_confidence():
    with pytest.raises(
        ValueError,
        match="CONFIDENCE_MUST_BE_BETWEEN_0_AND_1",
    ):
        confidence_interval(
            [1.0, 2.0],
            confidence=1.0,
        )

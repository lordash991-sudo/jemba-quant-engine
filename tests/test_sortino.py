import pytest

from jemba_core.quant import sortino_ratio


def test_calculates_positive_sortino():
    result = sortino_ratio(
        [0.02, 0.01, -0.005, 0.03],
        periods_per_year=252,
    )

    assert result > 0.0


def test_returns_zero_without_downside():
    assert sortino_ratio([0.01, 0.02, 0.03]) == 0.0


def test_rejects_non_finite_returns():
    with pytest.raises(
        ValueError,
        match="RETURNS_MUST_BE_FINITE",
    ):
        sortino_ratio([0.01, float("nan")])

import pytest

from jemba_core.quant import sharpe_ratio


def test_calculates_positive_sharpe():
    result = sharpe_ratio(
        [0.01, 0.02, -0.005, 0.015],
        periods_per_year=252,
    )

    assert result > 0.0


def test_returns_zero_for_constant_returns():
    assert sharpe_ratio([0.01, 0.01, 0.01]) == 0.0


def test_rejects_invalid_periods():
    with pytest.raises(
        ValueError,
        match="PERIODS_PER_YEAR_MUST_BE_POSITIVE",
    ):
        sharpe_ratio([0.01, 0.02], periods_per_year=0)

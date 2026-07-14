import pytest

from jemba_core.quant import (
    annualized_return,
    calmar_ratio,
)


def test_calculates_annualized_return():
    result = annualized_return(
        [100.0, 105.0, 110.0],
        periods_per_year=2,
    )

    assert result == pytest.approx(0.10)


def test_calmar_is_positive_for_profitable_curve():
    result = calmar_ratio(
        [100.0, 120.0, 110.0, 130.0],
        periods_per_year=3,
    )

    assert result > 0.0


def test_calmar_is_zero_without_drawdown():
    assert calmar_ratio([100.0, 110.0, 120.0]) == 0.0

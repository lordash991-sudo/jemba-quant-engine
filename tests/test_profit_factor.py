import math

import pytest

from jemba_core.quant import (
    gross_loss,
    gross_profit,
    profit_factor,
)


def test_calculates_profit_factor():
    trades = [100.0, -40.0, 50.0, -10.0]

    assert gross_profit(trades) == 150.0
    assert gross_loss(trades) == 50.0
    assert profit_factor(trades) == 3.0


def test_profit_factor_is_infinite_without_losses():
    assert math.isinf(profit_factor([10.0, 20.0]))


def test_profit_factor_is_zero_without_trades():
    assert profit_factor([]) == 0.0


def test_rejects_non_finite_trades():
    with pytest.raises(
        ValueError,
        match="TRADES_MUST_BE_FINITE",
    ):
        profit_factor([10.0, float("nan")])

import pytest

from jemba_core.quant import (
    average_loss,
    average_win,
    expectancy,
    loss_rate,
    win_rate,
)


def test_calculates_expectancy_metrics():
    trades = [100.0, -50.0, 50.0, -50.0]

    assert win_rate(trades) == pytest.approx(0.5)
    assert loss_rate(trades) == pytest.approx(0.5)
    assert average_win(trades) == pytest.approx(75.0)
    assert average_loss(trades) == pytest.approx(50.0)
    assert expectancy(trades) == pytest.approx(12.5)


def test_empty_trades_return_zero():
    assert win_rate([]) == 0.0
    assert loss_rate([]) == 0.0
    assert average_win([]) == 0.0
    assert average_loss([]) == 0.0
    assert expectancy([]) == 0.0

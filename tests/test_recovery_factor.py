import math

from jemba_core.quant import recovery_factor


def test_calculates_recovery_factor():
    result = recovery_factor([100.0, 120.0, 90.0, 130.0])

    assert result > 0.0


def test_recovery_is_infinite_without_drawdown():
    assert math.isinf(recovery_factor([100.0, 110.0, 120.0]))


def test_recovery_is_zero_without_profit():
    assert recovery_factor([100.0]) == 0.0

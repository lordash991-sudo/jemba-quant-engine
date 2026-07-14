import numpy as np
import pytest

from jemba_core.quant import (
    average_drawdown,
    drawdown_series,
    max_drawdown,
)


def test_calculates_drawdown_series():
    equity = [100.0, 120.0, 90.0, 130.0]

    result = drawdown_series(equity)

    np.testing.assert_allclose(
        result,
        [0.0, 0.0, -0.25, 0.0],
    )


def test_calculates_max_drawdown():
    assert max_drawdown([100.0, 120.0, 90.0, 130.0]) == pytest.approx(0.25)


def test_average_drawdown_is_zero_without_losses():
    assert average_drawdown([100.0, 110.0, 120.0]) == 0.0

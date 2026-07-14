import pytest

from jemba_core.quant import sqn


def test_calculates_positive_sqn():
    result = sqn([10.0, -5.0, 15.0, 5.0])

    assert result > 0.0


def test_sqn_is_zero_with_one_trade():
    assert sqn([10.0]) == 0.0


def test_rejects_non_finite_trades():
    with pytest.raises(
        ValueError,
        match="TRADES_MUST_BE_FINITE",
    ):
        sqn([10.0, float("inf")])

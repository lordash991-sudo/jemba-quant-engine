import pytest

from jemba_core.execution import (
    CommissionModel,
    OrderType,
)


def test_taker_commission():
    model = CommissionModel(taker_rate=0.001)

    result = model.calculate(
        notional=1_000.0,
        order_type=OrderType.MARKET,
    )

    assert result.trading_fee == pytest.approx(1.0)
    assert result.total_cost == pytest.approx(1.0)


def test_maker_commission():
    model = CommissionModel(maker_rate=0.0002)

    result = model.calculate(
        notional=1_000.0,
        order_type=OrderType.LIMIT,
    )

    assert result.trading_fee == pytest.approx(0.2)


def test_funding_fee():
    model = CommissionModel(funding_rate=0.0001)

    result = model.calculate(
        notional=10_000.0,
        order_type=OrderType.MARKET,
        funding_periods=2,
    )

    assert result.funding_fee == pytest.approx(2.0)


def test_rejects_negative_notional():
    model = CommissionModel()

    with pytest.raises(
        ValueError,
        match="NOTIONAL_MUST_BE_NON_NEGATIVE",
    ):
        model.calculate(
            notional=-1.0,
            order_type=OrderType.MARKET,
        )

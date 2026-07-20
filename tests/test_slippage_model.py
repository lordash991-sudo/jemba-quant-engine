import pytest

from jemba_core.execution import (
    OrderSide,
    SlippageModel,
    VolatilityRegime,
)


def test_buy_slippage_increases_price():
    model = SlippageModel(seed=7)

    result = model.calculate(
        price=100.0,
        side=OrderSide.BUY,
        volatility=VolatilityRegime.MEDIUM,
    )

    assert result.executed_price > 100.0
    assert result.amount > 0.0


def test_sell_slippage_decreases_price():
    model = SlippageModel(seed=7)

    result = model.calculate(
        price=100.0,
        side=OrderSide.SELL,
        volatility=VolatilityRegime.MEDIUM,
    )

    assert result.executed_price < 100.0


def test_seed_is_reproducible():
    first = SlippageModel(seed=10).calculate(
        price=100.0,
        side=OrderSide.BUY,
        volatility=VolatilityRegime.HIGH,
    )

    second = SlippageModel(seed=10).calculate(
        price=100.0,
        side=OrderSide.BUY,
        volatility=VolatilityRegime.HIGH,
    )

    assert first.rate == pytest.approx(second.rate)


def test_rejects_invalid_price():
    model = SlippageModel()

    with pytest.raises(
        ValueError,
        match="PRICE_MUST_BE_POSITIVE",
    ):
        model.calculate(
            price=0.0,
            side=OrderSide.BUY,
            volatility=VolatilityRegime.LOW,
        )

import pytest

from jemba_core.portfolio_optimizer.volatility_sizing import (
    volatility_position_size,
)


def test_basic_position_size():

    value = volatility_position_size(
        equity=10000,
        risk_fraction=0.01,
        atr=150,
        stop_multiplier=2,
    )

    assert value == pytest.approx(100 / 300)


def test_round_down():

    value = volatility_position_size(
        equity=10000,
        risk_fraction=0.01,
        atr=40,
        stop_multiplier=2,
        round_down=True,
    )

    assert value == 1


def test_invalid_equity():

    with pytest.raises(ValueError):
        volatility_position_size(
            equity=0,
            risk_fraction=0.01,
            atr=10,
            stop_multiplier=2,
        )


def test_invalid_atr():

    with pytest.raises(ValueError):
        volatility_position_size(
            equity=10000,
            risk_fraction=0.01,
            atr=0,
            stop_multiplier=2,
        )


def test_invalid_stop():

    with pytest.raises(ValueError):
        volatility_position_size(
            equity=10000,
            risk_fraction=0.01,
            atr=10,
            stop_multiplier=0,
        )


def test_invalid_point_value():

    with pytest.raises(ValueError):
        volatility_position_size(
            equity=10000,
            risk_fraction=0.01,
            atr=10,
            stop_multiplier=2,
            point_value=0,
        )


def test_invalid_risk():

    with pytest.raises(ValueError):
        volatility_position_size(
            equity=10000,
            risk_fraction=0,
            atr=10,
            stop_multiplier=2,
        )

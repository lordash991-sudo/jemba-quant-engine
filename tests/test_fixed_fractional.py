import pytest

from jemba_core.portfolio_optimizer import (
    fixed_fractional_position_size,
    fixed_fractional_risk_amount,
)


def test_calculates_risk_amount():
    value = fixed_fractional_risk_amount(
        equity=10_000.0,
        risk_fraction=0.02,
    )

    assert value == 200.0


def test_calculates_position_size():
    value = fixed_fractional_position_size(
        equity=10_000.0,
        risk_fraction=0.02,
        stop_distance=50.0,
        point_value=1.0,
    )

    assert value == 4.0


def test_uses_point_value():
    value = fixed_fractional_position_size(
        equity=10_000.0,
        risk_fraction=0.02,
        stop_distance=10.0,
        point_value=5.0,
    )

    assert value == 4.0


def test_rejects_invalid_equity():
    with pytest.raises(
        ValueError,
        match="EQUITY_MUST_BE_POSITIVE",
    ):
        fixed_fractional_risk_amount(
            equity=0.0,
            risk_fraction=0.02,
        )


def test_rejects_invalid_stop_distance():
    with pytest.raises(
        ValueError,
        match="STOP_DISTANCE_MUST_BE_POSITIVE",
    ):
        fixed_fractional_position_size(
            equity=10_000.0,
            risk_fraction=0.02,
            stop_distance=0.0,
        )

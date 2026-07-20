import pytest

from jemba_core.paper_broker import TradeManagementConfig


def test_default_configuration():
    config = TradeManagementConfig()

    assert config.break_even_trigger_rr == 1.0
    assert config.partial_take_profit_fraction == 0.50
    assert config.trailing_stop_trigger_rr == 1.50
    assert config.maximum_hold_minutes is None


def test_rejects_invalid_partial_fraction():
    with pytest.raises(
        ValueError,
        match=("PARTIAL_TAKE_PROFIT_FRACTION_MUST_BE_BETWEEN_0_AND_1"),
    ):
        TradeManagementConfig(partial_take_profit_fraction=1.0)


def test_rejects_invalid_time_stop():
    with pytest.raises(
        ValueError,
        match="MAXIMUM_HOLD_MINUTES_MUST_BE_POSITIVE",
    ):
        TradeManagementConfig(maximum_hold_minutes=0.0)

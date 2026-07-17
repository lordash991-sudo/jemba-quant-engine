import pytest

from jemba_core.trade_manager.partial_take_profit import (
    PartialTakeProfitResult,
    check_partial_take_profit,
)


def test_partial_take_profit_triggered():
    result = check_partial_take_profit(
        current_rr=2.0,
        trigger_rr=1.5,
    )

    assert result == PartialTakeProfitResult(
        True,
        "PARTIAL_TAKE_PROFIT",
    )


def test_partial_take_profit_not_triggered():
    result = check_partial_take_profit(
        current_rr=1.0,
        trigger_rr=2.0,
    )

    assert result == PartialTakeProfitResult(False)


def test_trigger_rr_validation():
    with pytest.raises(ValueError):
        check_partial_take_profit(
            current_rr=1,
            trigger_rr=0,
        )

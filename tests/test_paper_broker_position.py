import pytest

from jemba_core.paper_broker import (
    CloseReason,
    PaperPosition,
    PositionSide,
    PositionStatus,
)


def long_position():
    return PaperPosition(
        position_id="test-long",
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=110.0,
    )


def test_long_unrealized_profit():
    position = long_position()

    reason = position.update_price(105.0)

    assert reason is None
    assert position.unrealized_pnl == pytest.approx(10.0)


def test_long_stop_loss_trigger():
    position = long_position()

    reason = position.update_price(95.0)

    assert reason is CloseReason.STOP_LOSS


def test_long_take_profit_trigger():
    position = long_position()

    reason = position.update_price(110.0)

    assert reason is CloseReason.TAKE_PROFIT


def test_close_long_position():
    position = long_position()

    pnl = position.close(
        price=110.0,
        reason=CloseReason.MANUAL,
        commission=1.0,
    )

    assert pnl == pytest.approx(19.0)
    assert position.status is PositionStatus.CLOSED
    assert position.unrealized_pnl == 0.0


def test_short_profit():
    position = PaperPosition(
        position_id="test-short",
        symbol="BTCUSDT",
        side=PositionSide.SHORT,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=105.0,
        take_profit=90.0,
    )

    position.update_price(95.0)

    assert position.unrealized_pnl == pytest.approx(10.0)


def test_rejects_invalid_long_stop():
    with pytest.raises(
        ValueError,
        match="INVALID_LONG_STOP_LOSS",
    ):
        PaperPosition(
            position_id="bad",
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            entry_price=100.0,
            quantity=1.0,
            leverage=10,
            stop_loss=101.0,
            take_profit=110.0,
        )

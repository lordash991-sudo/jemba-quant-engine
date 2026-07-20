import pytest

from jemba_core.paper_broker import (
    CloseReason,
    PaperAccount,
    PaperPosition,
    PositionSide,
)


def test_account_snapshot():
    account = PaperAccount(1_000.0)

    position = PaperPosition(
        position_id="position",
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=110.0,
    )

    snapshot = account.snapshot(
        (position,),
        (),
    )

    assert snapshot.used_margin == pytest.approx(20.0)
    assert snapshot.free_margin == pytest.approx(980.0)
    assert snapshot.open_positions == 1


def test_apply_realized_profit():
    account = PaperAccount(1_000.0)

    position = PaperPosition(
        position_id="position",
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=110.0,
    )

    position.close(
        price=110.0,
        reason=CloseReason.MANUAL,
    )

    account.apply_closed_position(position)

    assert account.cash_balance == pytest.approx(1_020.0)
    assert account.realized_pnl == pytest.approx(20.0)


def test_rejects_insufficient_margin():
    account = PaperAccount(10.0)

    position = PaperPosition(
        position_id="position",
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=110.0,
    )

    with pytest.raises(
        ValueError,
        match="INSUFFICIENT_FREE_MARGIN",
    ):
        account.reserve_margin(position, ())

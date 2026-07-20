import pytest

from jemba_core.paper_broker import (
    CloseReason,
    PaperBroker,
    PositionSide,
    PositionStatus,
)


def open_long(broker):
    return broker.open_position(
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=110.0,
    )


def test_open_position():
    broker = PaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    assert position.status is PositionStatus.OPEN
    assert position.symbol == "BTCUSDT"
    assert len(broker.open_positions()) == 1


def test_market_update_changes_pnl():
    broker = PaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    broker.update_market_price(
        symbol="BTCUSDT",
        price=105.0,
    )

    updated = broker.get_position(position.position_id)

    assert updated.unrealized_pnl == pytest.approx(10.0)


def test_take_profit_closes_position():
    broker = PaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    broker.update_market_price(
        symbol="BTCUSDT",
        price=110.0,
    )

    closed = broker.get_position(position.position_id)

    assert closed.status is PositionStatus.CLOSED
    assert closed.close_reason is CloseReason.TAKE_PROFIT
    assert len(broker.open_positions()) == 0
    assert len(broker.closed_positions()) == 1


def test_stop_loss_closes_position():
    broker = PaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    broker.update_market_price(
        symbol="BTCUSDT",
        price=95.0,
    )

    closed = broker.get_position(position.position_id)

    assert closed.close_reason is CloseReason.STOP_LOSS
    assert closed.realized_pnl == pytest.approx(-10.0)


def test_manual_close():
    broker = PaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    result = broker.close_position(
        position.position_id,
        price=105.0,
    )

    assert result.status is PositionStatus.CLOSED
    assert result.close_reason is CloseReason.MANUAL
    assert result.realized_pnl == pytest.approx(10.0)


def test_rejects_duplicate_symbol():
    broker = PaperBroker(initial_balance=1_000.0)

    open_long(broker)

    with pytest.raises(
        ValueError,
        match="DUPLICATE_SYMBOL_POSITION",
    ):
        open_long(broker)


def test_account_updates_after_close():
    broker = PaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    broker.close_position(
        position.position_id,
        price=110.0,
    )

    account = broker.account_snapshot()

    assert account.cash_balance == pytest.approx(1_020.0)
    assert account.realized_pnl == pytest.approx(20.0)
    assert account.closed_positions == 1


def test_rejects_excessive_leverage():
    broker = PaperBroker(
        initial_balance=1_000.0,
        maximum_leverage=20,
    )

    with pytest.raises(
        ValueError,
        match="LEVERAGE_LIMIT_EXCEEDED",
    ):
        broker.open_position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            entry_price=100.0,
            quantity=1.0,
            leverage=50,
            stop_loss=95.0,
            take_profit=110.0,
        )

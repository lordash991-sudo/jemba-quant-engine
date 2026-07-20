from datetime import timedelta

import pytest

from jemba_core.paper_broker import (
    ManagedPaperBroker,
    PositionSide,
    PositionStatus,
    TradeManagementConfig,
    TradeManagementEventType,
)


def open_long(
    broker,
    *,
    quantity=2.0,
):
    return broker.open_position(
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=quantity,
        leverage=10,
        stop_loss=95.0,
        take_profit=120.0,
    )


def open_short(
    broker,
    *,
    quantity=2.0,
):
    return broker.open_position(
        symbol="ETHUSDT",
        side=PositionSide.SHORT,
        entry_price=100.0,
        quantity=quantity,
        leverage=10,
        stop_loss=105.0,
        take_profit=80.0,
    )


def test_initializes_management_state():
    broker = ManagedPaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    state = broker.management_state(position.position_id)

    assert state.initial_quantity == pytest.approx(2.0)
    assert state.risk_distance == pytest.approx(5.0)
    assert state.break_even_applied is False


def test_break_even_long():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=1.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    position = open_long(broker)

    events = broker.update_managed_price(
        symbol="BTCUSDT",
        price=105.0,
    )

    updated = broker.get_position(position.position_id)

    assert updated.stop_loss == pytest.approx(100.0)
    assert events[0].event_type is (TradeManagementEventType.BREAK_EVEN)


def test_partial_take_profit_long():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=1.0,
            partial_take_profit_fraction=0.50,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    position = open_long(
        broker,
        quantity=2.0,
    )

    events = broker.update_managed_price(
        symbol="BTCUSDT",
        price=105.0,
    )

    updated = broker.get_position(position.position_id)

    partial_events = [
        event
        for event in events
        if event.event_type is TradeManagementEventType.PARTIAL_TAKE_PROFIT
    ]

    assert len(partial_events) == 1
    assert updated.quantity == pytest.approx(1.0)
    assert partial_events[0].quantity == pytest.approx(1.0)
    assert partial_events[0].realized_pnl == pytest.approx(5.0)


def test_partial_take_profit_runs_once():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=1.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    position = open_long(broker)

    broker.update_managed_price(
        symbol="BTCUSDT",
        price=105.0,
    )

    broker.update_managed_price(
        symbol="BTCUSDT",
        price=106.0,
    )

    updated = broker.get_position(position.position_id)

    partial_events = [
        event
        for event in broker.management_events()
        if event.event_type is TradeManagementEventType.PARTIAL_TAKE_PROFIT
    ]

    assert len(partial_events) == 1
    assert updated.quantity == pytest.approx(1.0)


def test_long_trailing_stop():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=1.0,
            trailing_stop_distance_rr=0.50,
        ),
    )

    position = open_long(broker)

    broker.update_managed_price(
        symbol="BTCUSDT",
        price=110.0,
    )

    updated = broker.get_position(position.position_id)

    assert updated.stop_loss == pytest.approx(107.5)


def test_short_trailing_stop():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=1.0,
            trailing_stop_distance_rr=0.50,
        ),
    )

    position = open_short(broker)

    broker.update_managed_price(
        symbol="ETHUSDT",
        price=90.0,
    )

    updated = broker.get_position(position.position_id)

    assert updated.stop_loss == pytest.approx(92.5)


def test_time_stop_closes_position():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            maximum_hold_minutes=30.0,
        ),
    )

    position = open_long(broker)

    opened = broker.get_position(position.position_id).opened_at

    events = broker.update_managed_price(
        symbol="BTCUSDT",
        price=102.0,
        now=opened + timedelta(minutes=31),
    )

    closed = broker.get_position(position.position_id)

    assert closed.status is PositionStatus.CLOSED
    assert events[0].event_type is (TradeManagementEventType.TIME_STOP)


def test_stop_loss_still_closes_position():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    position = open_long(broker)

    events = broker.update_managed_price(
        symbol="BTCUSDT",
        price=95.0,
    )

    closed = broker.get_position(position.position_id)

    assert closed.status is PositionStatus.CLOSED
    assert events[-1].event_type is (TradeManagementEventType.STOP_LOSS)


def test_take_profit_still_closes_position():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    position = open_long(broker)

    events = broker.update_managed_price(
        symbol="BTCUSDT",
        price=120.0,
    )

    closed = broker.get_position(position.position_id)

    assert closed.status is PositionStatus.CLOSED
    assert events[-1].event_type is (TradeManagementEventType.TAKE_PROFIT)


def test_manual_close_removes_management_state():
    broker = ManagedPaperBroker(initial_balance=1_000.0)

    position = open_long(broker)

    broker.close_position(
        position.position_id,
        price=103.0,
    )

    with pytest.raises(
        KeyError,
        match="MANAGEMENT_STATE_NOT_FOUND",
    ):
        broker.management_state(position.position_id)


def test_partial_profit_updates_account():
    broker = ManagedPaperBroker(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=1.0,
            partial_take_profit_fraction=0.50,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    open_long(
        broker,
        quantity=2.0,
    )

    broker.update_managed_price(
        symbol="BTCUSDT",
        price=105.0,
    )

    account = broker.account_snapshot()

    assert account.realized_pnl == pytest.approx(5.0)
    assert account.cash_balance == pytest.approx(1_005.0)

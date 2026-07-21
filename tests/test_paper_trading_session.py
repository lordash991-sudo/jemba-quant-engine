from datetime import UTC, datetime, timedelta

import pytest

from jemba_core.paper_broker import (
    PositionSide,
    PositionStatus,
    TradeManagementConfig,
)
from jemba_core.paper_session import (
    MarketPriceUpdate,
    PaperSessionEventType,
    PaperSessionStatus,
    PaperTradeRequest,
    PaperTradingSession,
)


def valid_request(
    *,
    symbol="BTCUSDT",
):
    return PaperTradeRequest(
        symbol=symbol,
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=120.0,
    )


def test_start_session():
    session = PaperTradingSession(initial_balance=1_000.0)

    snapshot = session.start()

    assert snapshot.status is PaperSessionStatus.RUNNING
    assert snapshot.started_at is not None
    assert snapshot.events[0].event_type is (PaperSessionEventType.SESSION_STARTED)


def test_open_trade():
    session = PaperTradingSession(initial_balance=1_000.0)
    session.start()

    position = session.open_trade(valid_request())

    assert position is not None
    assert position.status is PositionStatus.OPEN

    snapshot = session.snapshot()

    assert snapshot.opened_positions == 1
    assert len(snapshot.open_positions) == 1


def test_rejects_trade_with_kill_switch():
    session = PaperTradingSession(initial_balance=1_000.0)
    session.start()
    session.activate_kill_switch()

    result = session.open_trade(valid_request())

    assert result is None

    snapshot = session.snapshot()

    assert snapshot.rejected_positions == 1


def test_process_price_updates_pnl():
    session = PaperTradingSession(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )
    session.start()

    position = session.open_trade(valid_request())

    assert position is not None

    result = session.process_price(
        MarketPriceUpdate(
            symbol="BTCUSDT",
            price=105.0,
            timestamp=datetime.now(UTC),
        )
    )

    updated = session.broker.get_position(position.position_id)

    assert updated.unrealized_pnl == pytest.approx(10.0)
    assert result.session_snapshot.processed_price_updates == 1


def test_take_profit_closes_position():
    session = PaperTradingSession(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )
    session.start()

    position = session.open_trade(valid_request())

    assert position is not None

    session.process_price(
        MarketPriceUpdate(
            symbol="BTCUSDT",
            price=120.0,
            timestamp=datetime.now(UTC),
        )
    )

    closed = session.broker.get_position(position.position_id)

    assert closed.status is PositionStatus.CLOSED
    assert len(session.snapshot().closed_positions) == 1


def test_break_even_event_is_recorded():
    session = PaperTradingSession(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=1.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )
    session.start()

    session.open_trade(valid_request())

    result = session.process_price(
        MarketPriceUpdate(
            symbol="BTCUSDT",
            price=105.0,
            timestamp=datetime.now(UTC),
        )
    )

    assert len(result.management_events) == 1
    assert result.session_snapshot.management_events == 1


def test_process_many_orders_by_time():
    session = PaperTradingSession(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )
    session.start()
    session.open_trade(valid_request())

    now = datetime.now(UTC)

    results = session.process_prices(
        [
            MarketPriceUpdate(
                symbol="BTCUSDT",
                price=103.0,
                timestamp=now + timedelta(minutes=2),
            ),
            MarketPriceUpdate(
                symbol="BTCUSDT",
                price=101.0,
                timestamp=now + timedelta(minutes=1),
            ),
        ]
    )

    assert results[0].price_update.price == 101.0
    assert results[1].price_update.price == 103.0


def test_manual_close():
    session = PaperTradingSession(initial_balance=1_000.0)
    session.start()

    position = session.open_trade(valid_request())

    assert position is not None

    closed = session.close_position(
        position.position_id,
        price=105.0,
    )

    assert closed.status is PositionStatus.CLOSED
    assert closed.realized_pnl == pytest.approx(10.0)


def test_stop_session():
    session = PaperTradingSession(initial_balance=1_000.0)
    session.start()

    snapshot = session.stop(completed=True)

    assert snapshot.status is PaperSessionStatus.COMPLETED
    assert snapshot.stopped_at is not None


def test_requires_running_session():
    session = PaperTradingSession(initial_balance=1_000.0)

    with pytest.raises(
        ValueError,
        match="SESSION_MUST_BE_RUNNING",
    ):
        session.open_trade(valid_request())


def test_rejects_duplicate_position():
    session = PaperTradingSession(initial_balance=1_000.0)
    session.start()

    first = session.open_trade(valid_request())
    second = session.open_trade(valid_request())

    assert first is not None
    assert second is None
    assert session.snapshot().rejected_positions == 1

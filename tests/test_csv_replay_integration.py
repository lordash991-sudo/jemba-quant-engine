from datetime import UTC, datetime

from jemba_core.market_replay import (
    CSVReplayEngine,
    ReplaySource,
)
from jemba_core.paper_broker import (
    PositionSide,
    TradeManagementConfig,
)
from jemba_core.paper_session import (
    MarketPriceUpdate,
    PaperTradeRequest,
    PaperTradingSession,
)


def test_replay_feeds_paper_session(tmp_path):
    csv_path = tmp_path / "BTCUSDT.csv"

    csv_path.write_text(
        "\n".join(
            [
                "timestamp,open,high,low,close,volume",
                "2026-01-01T01:00:00Z,100,102,99,101,1000",
                "2026-01-01T02:00:00Z,101,106,100,105,1200",
                "2026-01-01T03:00:00Z,105,121,104,120,1500",
            ]
        ),
        encoding="utf-8",
    )

    session = PaperTradingSession(
        initial_balance=1_000.0,
        management_config=TradeManagementConfig(
            break_even_trigger_rr=10.0,
            partial_take_profit_trigger_rr=10.0,
            trailing_stop_trigger_rr=10.0,
        ),
    )

    session.start(
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        )
    )

    position = session.open_trade(
        PaperTradeRequest(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            entry_price=100.0,
            quantity=1.0,
            leverage=10,
            stop_loss=95.0,
            take_profit=120.0,
        )
    )

    assert position is not None

    engine = CSVReplayEngine(
        [
            ReplaySource(
                symbol="BTCUSDT",
                file_path=csv_path,
            )
        ]
    )

    def feed_session(event):
        session.process_price(
            MarketPriceUpdate(
                symbol=event.candle.symbol,
                price=event.candle.close,
                timestamp=event.candle.timestamp,
            )
        )

    engine.subscribe(feed_session)
    engine.play()

    closed = session.broker.get_position(position.position_id)

    assert closed.realized_pnl == 20.0
    assert len(session.snapshot().closed_positions) == 1

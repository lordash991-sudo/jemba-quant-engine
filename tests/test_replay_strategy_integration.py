from datetime import UTC, datetime

from jemba_core.market_replay import (
    CSVReplayEngine,
    ReplaySource,
)
from jemba_core.paper_broker import (
    TradeManagementConfig,
)
from jemba_core.paper_session import PaperTradingSession
from jemba_core.replay_runner import (
    MovingAverageCrossStrategy,
    ReplayStrategyRunner,
)


def test_moving_average_replay_integration(tmp_path):
    path = tmp_path / "BTCUSDT.csv"

    rows = [
        "timestamp,open,high,low,close,volume",
        "2026-01-01T01:00:00Z,100,101,99,100,1000",
        "2026-01-01T02:00:00Z,99,100,98,99,1000",
        "2026-01-01T03:00:00Z,98,99,97,98,1000",
        "2026-01-01T04:00:00Z,101,102,100,101,1000",
        "2026-01-01T05:00:00Z,105,106,104,105,1000",
        "2026-01-01T06:00:00Z,106,107,105,106,1000",
    ]

    path.write_text(
        "\n".join(rows),
        encoding="utf-8",
    )

    replay = CSVReplayEngine(
        [
            ReplaySource(
                symbol="BTCUSDT",
                file_path=path,
            )
        ]
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

    runner = ReplayStrategyRunner(
        replay_engine=replay,
        session=session,
        strategy=MovingAverageCrossStrategy(
            fast_period=2,
            slow_period=3,
            quantity=1.0,
            leverage=10,
            stop_loss_percent=0.02,
            take_profit_percent=0.04,
            confidence=80.0,
        ),
    )

    result = runner.run()

    assert result.statistics.processed_candles == 6
    assert result.statistics.generated_signals >= 1
    assert result.statistics.opened_positions >= 1

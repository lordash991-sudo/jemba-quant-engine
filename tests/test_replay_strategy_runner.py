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
    PaperTradingSession,
)
from jemba_core.replay_runner import (
    ReplayRunnerStatus,
    ReplayStrategy,
    ReplayStrategyContext,
    ReplayStrategyRunner,
    ReplayTradeSignal,
)


class OneSignalStrategy(ReplayStrategy):
    def __init__(self):
        self.generated = False

    def on_candle(
        self,
        context: ReplayStrategyContext,
    ):
        if self.generated:
            return None

        self.generated = True

        return ReplayTradeSignal(
            symbol=context.candle.symbol,
            side=PositionSide.LONG,
            confidence=90.0,
            quantity=1.0,
            leverage=10,
            stop_loss=context.candle.close * 0.95,
            take_profit=context.candle.close * 1.10,
            reason="TEST_SIGNAL",
        )


def create_csv(tmp_path):
    path = tmp_path / "BTCUSDT.csv"

    path.write_text(
        "\n".join(
            [
                "timestamp,open,high,low,close,volume",
                "2026-01-01T01:00:00Z,100,101,99,100,1000",
                "2026-01-01T02:00:00Z,100,106,99,105,1200",
                "2026-01-01T03:00:00Z,105,112,104,110,1500",
            ]
        ),
        encoding="utf-8",
    )

    return path


def create_runner(tmp_path, minimum_confidence=70.0):
    replay = CSVReplayEngine(
        [
            ReplaySource(
                symbol="BTCUSDT",
                file_path=create_csv(tmp_path),
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

    return ReplayStrategyRunner(
        replay_engine=replay,
        session=session,
        strategy=OneSignalStrategy(),
        minimum_confidence=minimum_confidence,
    )


def test_runner_processes_candles(tmp_path):
    runner = create_runner(tmp_path)

    result = runner.run()

    assert result.status is ReplayRunnerStatus.COMPLETED
    assert result.statistics.processed_candles == 3
    assert result.statistics.generated_signals == 1
    assert result.statistics.approved_signals == 1


def test_runner_opens_and_closes_trade(tmp_path):
    runner = create_runner(tmp_path)

    result = runner.run()

    assert result.statistics.opened_positions == 1
    assert result.statistics.closed_positions == 1
    assert result.statistics.realized_pnl == 10.0
    assert result.statistics.final_equity == 1_010.0


def test_runner_rejects_low_confidence(tmp_path):
    runner = create_runner(
        tmp_path,
        minimum_confidence=95.0,
    )

    result = runner.run()

    assert result.statistics.approved_signals == 0
    assert result.statistics.rejected_signals == 1
    assert result.statistics.opened_positions == 0


def test_signal_filter_can_reject(tmp_path):
    runner = create_runner(tmp_path)

    runner.signal_filter = lambda signal, context: (
        False,
        "CUSTOM_FILTER_REJECTED",
    )

    result = runner.run()

    assert result.statistics.rejected_signals == 1
    assert result.signals[0].reason == "CUSTOM_FILTER_REJECTED"

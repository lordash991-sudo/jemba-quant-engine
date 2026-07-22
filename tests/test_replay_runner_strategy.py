from datetime import UTC, datetime, timedelta

from jemba_core.market_replay import Candle
from jemba_core.paper_broker import PositionSide
from jemba_core.replay_runner import (
    MovingAverageCrossStrategy,
    ReplayStrategyContext,
)


def context(index, close):
    timestamp = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    ) + timedelta(hours=index)

    candle = Candle(
        symbol="BTCUSDT",
        timestamp=timestamp,
        open=close,
        high=close + 1.0,
        low=close - 1.0,
        close=close,
        volume=1_000.0,
    )

    return ReplayStrategyContext(
        candle=candle,
        candle_index=index,
        symbol_candle_index=index,
        has_open_position=False,
        account_equity=1_000.0,
        free_margin=1_000.0,
    )


def test_moving_average_strategy_generates_signal():
    strategy = MovingAverageCrossStrategy(
        fast_period=2,
        slow_period=3,
    )

    closes = [
        100.0,
        99.0,
        98.0,
        101.0,
    ]

    signals = [
        strategy.on_candle(context(index, close)) for index, close in enumerate(closes)
    ]

    signal = signals[-1]

    assert signal is not None
    assert signal.side is PositionSide.LONG
    assert signal.stop_loss < 101.0
    assert signal.take_profit > 101.0


def test_strategy_holds_during_warmup():
    strategy = MovingAverageCrossStrategy(
        fast_period=2,
        slow_period=4,
    )

    assert strategy.on_candle(context(0, 100.0)) is None

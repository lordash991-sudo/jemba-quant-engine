from datetime import UTC, datetime

import pytest

from jemba_core.market_replay import Candle
from jemba_core.paper_broker import PositionSide
from jemba_core.replay_runner import (
    ReplayStrategyContext,
    ReplayTradeSignal,
)


def candle():
    return Candle(
        symbol="BTCUSDT",
        timestamp=datetime.now(UTC),
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=1_000.0,
    )


def test_signal_normalizes_symbol():
    signal = ReplayTradeSignal(
        symbol=" btcusdt ",
        side=PositionSide.LONG,
        confidence=80.0,
        quantity=1.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=115.0,
    )

    assert signal.symbol == "BTCUSDT"


def test_signal_rejects_invalid_confidence():
    with pytest.raises(
        ValueError,
        match=("CONFIDENCE_MUST_BE_BETWEEN_0_AND_100"),
    ):
        ReplayTradeSignal(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            confidence=101.0,
            quantity=1.0,
            leverage=10,
            stop_loss=95.0,
            take_profit=115.0,
        )


def test_context_accepts_previous_candle():
    current = candle()

    context = ReplayStrategyContext(
        candle=current,
        candle_index=5,
        symbol_candle_index=3,
        has_open_position=False,
        account_equity=1_000.0,
        free_margin=900.0,
        previous_candle=current,
    )

    assert context.previous_candle is current

from datetime import UTC, datetime

import pytest

from jemba_core.market_replay import (
    Candle,
    MarketSession,
    ReplayConfig,
    ReplaySpeed,
    is_in_market_session,
)


def test_candle_normalizes_symbol():
    candle = Candle(
        symbol=" btcusdt ",
        timestamp=datetime.now(UTC),
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=1_000.0,
    )

    assert candle.symbol == "BTCUSDT"


def test_candle_rejects_invalid_high():
    with pytest.raises(
        ValueError,
        match="INVALID_CANDLE_HIGH",
    ):
        Candle(
            symbol="BTCUSDT",
            timestamp=datetime.now(UTC),
            open=100.0,
            high=99.0,
            low=90.0,
            close=105.0,
            volume=1_000.0,
        )


def test_replay_config_rejects_invalid_range():
    start = datetime(2026, 1, 2, tzinfo=UTC)
    end = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="END_AT_MUST_NOT_PRECEDE_START_AT",
    ):
        ReplayConfig(
            start_at=start,
            end_at=end,
        )


def test_market_sessions():
    asia = datetime(
        2026,
        1,
        1,
        3,
        0,
        tzinfo=UTC,
    )
    london = datetime(
        2026,
        1,
        1,
        9,
        0,
        tzinfo=UTC,
    )
    new_york = datetime(
        2026,
        1,
        1,
        15,
        0,
        tzinfo=UTC,
    )

    assert is_in_market_session(
        asia,
        MarketSession.ASIA,
    )
    assert is_in_market_session(
        london,
        MarketSession.LONDON,
    )
    assert is_in_market_session(
        new_york,
        MarketSession.NEW_YORK,
    )


def test_default_speed():
    config = ReplayConfig()

    assert config.speed is ReplaySpeed.X1000

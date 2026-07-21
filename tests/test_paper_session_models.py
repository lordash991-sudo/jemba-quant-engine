from datetime import UTC, datetime

import pytest

from jemba_core.paper_broker import PositionSide
from jemba_core.paper_session import (
    MarketPriceUpdate,
    PaperTradeRequest,
)


def test_market_price_normalizes_symbol():
    update = MarketPriceUpdate(
        symbol=" btcusdt ",
        price=100.0,
        timestamp=datetime.now(UTC),
    )

    assert update.symbol == "BTCUSDT"


def test_market_price_rejects_naive_timestamp():
    with pytest.raises(
        ValueError,
        match="TIMESTAMP_MUST_BE_TIMEZONE_AWARE",
    ):
        MarketPriceUpdate(
            symbol="BTCUSDT",
            price=100.0,
            timestamp=datetime.now(),
        )


def test_trade_request_normalizes_symbol():
    request = PaperTradeRequest(
        symbol=" ethusdt ",
        side=PositionSide.LONG,
        entry_price=100.0,
        quantity=1.0,
        leverage=10,
        stop_loss=95.0,
        take_profit=110.0,
    )

    assert request.symbol == "ETHUSDT"


def test_trade_request_rejects_invalid_leverage():
    with pytest.raises(
        ValueError,
        match="LEVERAGE_MUST_BE_POSITIVE",
    ):
        PaperTradeRequest(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            entry_price=100.0,
            quantity=1.0,
            leverage=0,
            stop_loss=95.0,
            take_profit=110.0,
        )

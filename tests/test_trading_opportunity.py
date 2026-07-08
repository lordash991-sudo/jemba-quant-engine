from jemba_core.engine.trading_opportunity import TradingOpportunity


def test_trading_opportunity_tradeable():
    opportunity = TradingOpportunity(
        symbol="BTC-USDT",
        timeframe="1h",
        action="BUY",
        entry=100,
        stop_loss=95,
        take_profit=110,
        confidence=0.90,
        ai_probability=0.92,
    )

    assert opportunity.is_tradeable() is True


def test_trading_opportunity_not_tradeable_when_hold():
    opportunity = TradingOpportunity(
        symbol="BTC-USDT",
        timeframe="1h",
        action="HOLD",
        entry=100,
        stop_loss=95,
        take_profit=110,
        confidence=0.90,
    )

    assert opportunity.is_tradeable() is False

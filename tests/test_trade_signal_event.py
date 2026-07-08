from jemba_core.events.trade_signal_event import TradeSignalEvent


def test_trade_signal_event():

    event = TradeSignalEvent(
        source="Predictor",
        symbol="BTC-USDT",
        timeframe="1h",
        side="BUY",
        entry=104250.5,
        stop_loss=103900.0,
        take_profit=105800.0,
        confidence=0.93,
        strategy="JEMBA_AI_V1",
    )

    assert event.event_type == "TradeSignalEvent"
    assert event.symbol == "BTC-USDT"
    assert event.side == "BUY"
    assert event.entry == 104250.5
    assert event.stop_loss == 103900.0
    assert event.take_profit == 105800.0
    assert event.confidence == 0.93
    assert event.strategy == "JEMBA_AI_V1"

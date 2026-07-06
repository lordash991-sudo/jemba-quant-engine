from jemba_core.events.trade_signal_event import TradeSignalEvent
from jemba_core.signals.signal_engine import SignalEngine


def test_generate_buy_signal():
    engine = SignalEngine()

    signal = engine.generate_signal(
        symbol="BTC-USDT",
        timeframe="1h",
        action="BUY",
        entry=100,
        confidence=0.90,
        atr=5,
    )

    assert signal.action == "BUY"
    assert signal.stop_loss == 95
    assert signal.take_profit == 110


def test_generate_sell_signal():
    engine = SignalEngine()

    signal = engine.generate_signal(
        symbol="BTC-USDT",
        timeframe="1h",
        action="SELL",
        entry=100,
        confidence=0.90,
        atr=5,
    )

    assert signal.action == "SELL"
    assert signal.stop_loss == 105
    assert signal.take_profit == 90


def test_hold_returns_none():
    engine = SignalEngine()

    signal = engine.generate_signal(
        symbol="BTC-USDT",
        timeframe="1h",
        action="HOLD",
        entry=100,
        confidence=0.50,
        atr=5,
    )

    assert signal is None


def test_signal_to_trade_signal_event():
    engine = SignalEngine()

    signal = engine.generate_signal(
        symbol="BTC-USDT",
        timeframe="1h",
        action="BUY",
        entry=100,
        confidence=0.90,
        atr=5,
    )

    event = engine.to_event(signal)

    assert isinstance(event, TradeSignalEvent)
    assert event.event_type == "TradeSignalEvent"
    assert event.symbol == "BTC-USDT"
    assert event.side == "BUY"
    assert event.entry == 100
    assert event.stop_loss == 95
    assert event.take_profit == 110

from jemba_core.events.prediction_event import PredictionEvent


def test_prediction_event():
    event = PredictionEvent(
        source="Predictor",
        symbol="BTC-USDT",
        timeframe="1h",
        action="BUY",
        confidence=0.91,
        probability=0.95,
        model="RandomForest",
    )

    assert event.event_type == "PredictionEvent"
    assert event.symbol == "BTC-USDT"
    assert event.action == "BUY"
    assert event.model == "RandomForest"

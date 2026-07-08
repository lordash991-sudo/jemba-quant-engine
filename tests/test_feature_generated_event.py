from jemba_core.events.feature_generated_event import FeatureGeneratedEvent


def test_feature_generated_event():
    event = FeatureGeneratedEvent(
        source="FeatureEngine",
        symbol="BTC-USDT",
        timeframe="1h",
        rows=500,
        columns=34,
        last_close=63250.5,
    )

    assert event.event_type == "FeatureGeneratedEvent"
    assert event.symbol == "BTC-USDT"
    assert event.timeframe == "1h"
    assert event.rows == 500
    assert event.columns == 34
    assert event.last_close == 63250.5

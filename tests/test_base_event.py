from jemba_core.events.base_event import BaseEvent


def test_create_event():
    event = BaseEvent(
        event_type="Prediction",
        source="Predictor"
    )

    assert event.event_type == "Prediction"
    assert event.source == "Predictor"
    assert event.version == "1.0"
    assert event.event_id is not None
    assert event.timestamp is not None
    assert event.metadata == {}

from jemba_core.events.base_event import BaseEvent
from jemba_core.events.event_bus import EventBus


def test_publish_to_one_subscriber():
    bus = EventBus()
    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(BaseEvent, handler)

    event = BaseEvent(event_type="Test", source="UnitTest")
    bus.publish(event)

    assert received == [event]


def test_publish_to_multiple_subscribers():
    bus = EventBus()
    received = []

    for i in range(5):
        bus.subscribe(BaseEvent, lambda event, i=i: received.append((i, event)))

    event = BaseEvent(event_type="Test", source="UnitTest")
    bus.publish(event)

    assert len(received) == 5


def test_subscriber_exception_does_not_stop_others():
    bus = EventBus()
    received = []

    def broken_handler(event):
        raise ValueError("boom")

    def good_handler(event):
        received.append(event)

    bus.subscribe(BaseEvent, broken_handler)
    bus.subscribe(BaseEvent, good_handler)

    event = BaseEvent(event_type="Test", source="UnitTest")
    bus.publish(event)

    assert received == [event]


def test_unsubscribe():
    bus = EventBus()
    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(BaseEvent, handler)
    bus.unsubscribe(BaseEvent, handler)

    event = BaseEvent(event_type="Test", source="UnitTest")
    bus.publish(event)

    assert received == []


def test_clear():
    bus = EventBus()
    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(BaseEvent, handler)
    bus.clear()

    event = BaseEvent(event_type="Test", source="UnitTest")
    bus.publish(event)

    assert received == []

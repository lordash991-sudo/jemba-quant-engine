from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event):
        event_type = type(event)

        for handler in list(self._subscribers[event_type]):
            try:
                handler(event)
            except Exception:
                continue

    def clear(self):
        self._subscribers.clear()

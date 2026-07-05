from jemba_core.events.base_event import BaseEvent


class FeatureGeneratedEvent(BaseEvent):

    def __init__(
        self,
        source: str,
        symbol: str,
        timeframe: str,
        rows: int,
        columns: int,
        last_close: float = 0.0,
        metadata: dict | None = None,
    ):
        super().__init__(
            event_type="FeatureGeneratedEvent",
            source=source,
            metadata=metadata or {},
        )

        self.symbol = symbol
        self.timeframe = timeframe
        self.rows = rows
        self.columns = columns
        self.last_close = last_close

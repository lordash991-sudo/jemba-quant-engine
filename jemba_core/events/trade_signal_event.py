from jemba_core.events.base_event import BaseEvent


class TradeSignalEvent(BaseEvent):
    def __init__(
        self,
        source: str,
        symbol: str,
        timeframe: str,
        side: str,
        entry: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
        strategy: str,
        metadata: dict | None = None,
    ):
        super().__init__(
            event_type="TradeSignalEvent",
            source=source,
            metadata=metadata or {},
        )

        self.symbol = symbol
        self.timeframe = timeframe
        self.side = side
        self.entry = entry
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.confidence = confidence
        self.strategy = strategy

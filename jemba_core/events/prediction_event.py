from jemba_core.events.base_event import BaseEvent


class PredictionEvent(BaseEvent):

    def __init__(
        self,
        source: str,
        symbol: str,
        timeframe: str,
        action: str,
        confidence: float,
        probability: float,
        model: str,
        metadata: dict | None = None,
    ):
        super().__init__(
            event_type="PredictionEvent",
            source=source,
            metadata=metadata or {},
        )

        self.symbol = symbol
        self.timeframe = timeframe
        self.action = action
        self.confidence = confidence
        self.probability = probability
        self.model = model

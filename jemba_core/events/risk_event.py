from jemba_core.events.base_event import BaseEvent


class RiskEvent(BaseEvent):

    def __init__(
        self,
        source: str,
        approved: bool,
        reason: str = "",
        risk_percent: float = 0.0,
        drawdown: float = 0.0,
        consecutive_losses: int = 0,
        metadata: dict | None = None,
    ):
        super().__init__(
            event_type="RiskEvent",
            source=source,
            metadata=metadata or {},
        )

        self.approved = approved
        self.reason = reason
        self.risk_percent = risk_percent
        self.drawdown = drawdown
        self.consecutive_losses = consecutive_losses

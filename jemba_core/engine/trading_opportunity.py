from dataclasses import dataclass, field


@dataclass
class TradingOpportunity:
    symbol: str
    timeframe: str
    action: str

    entry: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0

    confidence: float = 0.0
    ai_probability: float = 0.0

    position_size: float = 0.0
    approved: bool = False

    reason: str = ""
    metadata: dict = field(default_factory=dict)

    def is_tradeable(self):
        return (
            self.action in ["BUY", "SELL"]
            and self.confidence > 0
            and self.entry > 0
            and self.stop_loss > 0
            and self.take_profit > 0
        )

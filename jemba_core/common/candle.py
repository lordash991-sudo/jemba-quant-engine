from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def range(self) -> float:
        return self.high - self.low

    def body(self) -> float:
        return abs(self.close - self.open)

    def is_bullish(self) -> bool:
        return self.close > self.open

    def is_bearish(self) -> bool:
        return self.close < self.open

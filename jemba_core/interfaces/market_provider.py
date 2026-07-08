from abc import ABC, abstractmethod

from jemba_core.common.candle import Candle


class MarketProvider(ABC):
    @abstractmethod
    def get_candles(
        self, symbol: str, timeframe: str, limit: int = 500
    ) -> list[Candle]:
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        pass

    @abstractmethod
    def get_symbols(self) -> list[str]:
        pass

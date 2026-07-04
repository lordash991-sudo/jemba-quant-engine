from jemba_core.providers.bingx_provider import BingXProvider
from jemba_core.database.sqlite_storage import SQLiteStorage


class MarketDataManager:

    def __init__(self):
        self.provider = BingXProvider()
        self.storage = SQLiteStorage()

    def update(self, symbol: str, timeframe: str, limit: int = 500):
        candles = self.provider.get_candles(symbol, timeframe, limit)
        inserted = self.storage.save_candles(candles)

        return {
            "downloaded": len(candles),
            "inserted": inserted,
            "database": self.storage.count_candles()
        }

    def total(self):
        return self.storage.count_candles()

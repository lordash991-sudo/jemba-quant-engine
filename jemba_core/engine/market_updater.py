from sqlalchemy import text

from jemba_core.providers.bingx_updater import BingXUpdater
from jemba_core.database.sqlite_storage import SQLiteStorage


class MarketUpdater:

    def __init__(self):
        self.provider = BingXUpdater()
        self.storage = SQLiteStorage()

    def candle_exists(self, candle):
        query = text("""
            SELECT COUNT(*)
            FROM candles
            WHERE symbol = :symbol
              AND timeframe = :timeframe
              AND timestamp = :timestamp
        """)

        with self.storage.engine.begin() as conn:
            result = conn.execute(
                query,
                {
                    "symbol": candle.symbol,
                    "timeframe": candle.timeframe,
                    "timestamp": candle.timestamp.isoformat()
                }
            )

            return result.scalar() > 0

    def update(self, symbol="BTC-USDT", timeframe="1h"):
        candle = self.provider.latest_closed_candle(symbol, timeframe)

        if candle is None:
            return False

        if self.candle_exists(candle):
            return False

        inserted = self.storage.save_candles([candle])

        return inserted > 0

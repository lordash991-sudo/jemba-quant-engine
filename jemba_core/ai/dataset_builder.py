
from jemba_core.database.candle_repository import CandleRepository
from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.features.feature_engine import FeatureEngine


class DatasetBuilder:

    def __init__(self):
        self.storage = SQLiteStorage()
        self.repository = CandleRepository(self.storage)

    def build(self,
              symbol="BTC-USDT",
              timeframe="1h",
              limit=5000):

        df = self.repository.load_candles(
            symbol,
            timeframe,
            limit
        )

        df["EMA20"] = FeatureEngine.ema(df,20)
        df["EMA50"] = FeatureEngine.ema(df,50)
        df["ATR"] = FeatureEngine.atr(df)
        df["BODY"] = FeatureEngine.body(df)
        df["BULLISH"] = FeatureEngine.bullish(df)
        df["BEARISH"] = FeatureEngine.bearish(df)

        return df

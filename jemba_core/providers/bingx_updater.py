from jemba_core.providers.bingx_provider import BingXProvider


class BingXUpdater:
    def __init__(self):
        self.provider = BingXProvider()

    def latest_closed_candle(self, symbol="BTC-USDT", timeframe="1h"):
        candles = self.provider.get_candles(symbol, timeframe, limit=3)

        if not candles:
            return None

        if len(candles) >= 2:
            return candles[-2]

        return candles[-1]

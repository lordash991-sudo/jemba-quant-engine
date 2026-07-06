import requests


class BingXProvider:

    BASE_URL = "https://open-api.bingx.com"

    def __init__(self, timeout=10):
        self.timeout = timeout

    def ping(self):
        r = requests.get(
            self.BASE_URL + "/openApi/swap/v2/server/time",
            timeout=self.timeout,
        )
        return r.status_code == 200

    def get_price(self, symbol):
        r = requests.get(
            self.BASE_URL + "/openApi/swap/v2/quote/price",
            params={"symbol": symbol},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_candles(self, symbol, timeframe, limit=500):
        r = requests.get(
            self.BASE_URL + "/openApi/swap/v3/quote/klines",
            params={
                "symbol": symbol,
                "interval": timeframe,
                "limit": limit,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_latest(self, symbol, timeframe):
        data = self.get_candles(symbol, timeframe, limit=1)

        if not data:
            return None

        return data[-1]

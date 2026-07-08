from __future__ import annotations

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

    def _extract_data(self, payload):
        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):
            data = payload.get("data", payload)

            if isinstance(data, dict) and "list" in data:
                return data["list"]

            return data

        return payload

    def get_price(self, symbol):
        r = requests.get(
            self.BASE_URL + "/openApi/swap/v2/quote/price",
            params={"symbol": symbol},
            timeout=self.timeout,
        )
        r.raise_for_status()

        return self._extract_data(r.json())

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

        return self._extract_data(r.json())

    def get_latest(self, symbol, timeframe):
        candles = self.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            limit=1,
        )

        if not candles:
            return None

        if isinstance(candles, list):
            return candles[-1]

        return candles

from datetime import datetime, timezone
from typing import List

import requests

from jemba_core.common.candle import Candle
from jemba_core.interfaces.market_provider import MarketProvider


class BingXProvider(MarketProvider):
    BASE_URL = "https://open-api.bingx.com"

    def get_candles(self, symbol: str, timeframe: str, limit: int = 500) -> List[Candle]:
        endpoint = "/openApi/swap/v3/quote/klines"

        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": limit,
        }

        response = requests.get(
            self.BASE_URL + endpoint,
            params=params,
            timeout=15,
        )

        response.raise_for_status()
        payload = response.json()

        if payload.get("code") != 0:
            raise RuntimeError(f"BingX error: {payload}")

        raw_candles = payload.get("data", [])

        candles: List[Candle] = []

        for item in raw_candles:
            candles.append(
                Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=datetime.fromtimestamp(int(item["time"]) / 1000, tz=timezone.utc),
                    open=float(item["open"]),
                    high=float(item["high"]),
                    low=float(item["low"]),
                    close=float(item["close"]),
                    volume=float(item["volume"]),
                )
            )

        candles.sort(key=lambda candle: candle.timestamp)

        return candles

    def get_latest_price(self, symbol: str) -> float:
        endpoint = "/openApi/swap/v2/quote/price"

        params = {
            "symbol": symbol,
        }

        response = requests.get(
            self.BASE_URL + endpoint,
            params=params,
            timeout=15,
        )

        response.raise_for_status()
        payload = response.json()

        if payload.get("code") != 0:
            raise RuntimeError(f"BingX error: {payload}")

        data = payload.get("data", {})
        return float(data["price"])

    def get_symbols(self) -> List[str]:
        endpoint = "/openApi/swap/v2/quote/contracts"

        response = requests.get(
            self.BASE_URL + endpoint,
            timeout=15,
        )

        response.raise_for_status()
        payload = response.json()

        if payload.get("code") != 0:
            raise RuntimeError(f"BingX error: {payload}")

        data = payload.get("data", [])
        return [item["symbol"] for item in data if "symbol" in item]

from __future__ import annotations

import pandas as pd


class TrendFeatures:
    EMAS = (20, 50, 100, 200)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        if "close" not in data.columns:
            raise ValueError("Missing 'close' column")

        for period in self.EMAS:
            data[f"ema_{period}"] = data["close"].ewm(span=period, adjust=False).mean()

        data["ema20_above_ema50"] = (data["ema_20"] > data["ema_50"]).astype(int)
        data["ema50_above_ema200"] = (data["ema_50"] > data["ema_200"]).astype(int)

        data["distance_ema20"] = (data["close"] - data["ema_20"]) / data["ema_20"]
        data["distance_ema50"] = (data["close"] - data["ema_50"]) / data["ema_50"]
        data["distance_ema200"] = (data["close"] - data["ema_200"]) / data["ema_200"]

        return data

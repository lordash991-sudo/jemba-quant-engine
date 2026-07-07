from __future__ import annotations

import pandas as pd


class FeatureEngine:

    def __init__(self):
        pass

    def build(self, candles):

        if candles is None:
            return pd.DataFrame()

        df = pd.DataFrame(candles)

        if df.empty:
            return df

        numeric = [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        for col in numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col])

        return df

    def latest(self, candles):

        df = self.build(candles)

        if df.empty:
            return None

        return df.iloc[-1].to_dict()
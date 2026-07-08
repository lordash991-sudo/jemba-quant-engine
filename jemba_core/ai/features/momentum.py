from __future__ import annotations

import pandas as pd


class MomentumFeatures:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        if "close" not in data.columns:
            raise ValueError("Missing 'close' column")

        delta = data["close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss.replace(0, pd.NA)

        data["rsi_14"] = 100 - (100 / (1 + rs))

        data["roc_10"] = data["close"].pct_change(10)

        data["momentum_5"] = data["close"] - data["close"].shift(5)
        data["momentum_10"] = data["close"] - data["close"].shift(10)
        data["momentum_20"] = data["close"] - data["close"].shift(20)

        return data

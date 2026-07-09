from __future__ import annotations

import pandas as pd


class MomentumFeatures:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        if "close" not in data.columns:
            raise ValueError("Missing 'close' column")

        close = data["close"]

        # -----------------------
        # RSI(14)
        # -----------------------
        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss.replace(0, pd.NA)

        data["rsi_14"] = 100 - (100 / (1 + rs))

        # -----------------------
        # ROC
        # -----------------------

        data["roc_10"] = close.pct_change(10)

        # -----------------------
        # Momentum
        # -----------------------

        data["momentum_5"] = close - close.shift(5)
        data["momentum_10"] = close - close.shift(10)
        data["momentum_20"] = close - close.shift(20)

        # -----------------------
        # EMA
        # -----------------------

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()

        # -----------------------
        # MACD
        # -----------------------

        data["macd"] = ema12 - ema26

        data["macd_signal"] = data["macd"].ewm(span=9, adjust=False).mean()

        data["macd_histogram"] = data["macd"] - data["macd_signal"]

        return data

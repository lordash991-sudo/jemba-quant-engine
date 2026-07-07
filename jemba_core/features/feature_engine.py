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
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df["ema_20"] = self.ema(df["close"], 20)
        df["ema_50"] = self.ema(df["close"], 50)
        df["ema_200"] = self.ema(df["close"], 200)

        df["atr_14"] = self.atr(df, 14)
        df["rsi_14"] = self.rsi(df["close"], 14)

        df["return_1"] = df["close"].pct_change()
        df["volatility_20"] = df["return_1"].rolling(20).std()
        df["momentum_10"] = df["close"] - df["close"].shift(10)
        df["volume_sma_20"] = df["volume"].rolling(20).mean()

        return df

    def latest(self, candles):
        df = self.build(candles)

        if df.empty:
            return None

        return df.iloc[-1].to_dict()

    @staticmethod
    def ema(series, period):
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def atr(df, period=14):
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()

        true_range = pd.concat(
            [high_low, high_close, low_close],
            axis=1,
        ).max(axis=1)

        return true_range.rolling(period).mean()

    @staticmethod
    def rsi(series, period=14):
        delta = series.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        return 100 - (100 / (1 + rs))

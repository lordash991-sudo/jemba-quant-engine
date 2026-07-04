import pandas as pd


class FeatureEngine:

    @staticmethod
    def ema(df: pd.DataFrame, period: int):

        return df["close"].ewm(span=period, adjust=False).mean()

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14):

        high_low = df["high"] - df["low"]

        high_close = (df["high"] - df["close"].shift()).abs()

        low_close = (df["low"] - df["close"].shift()).abs()

        tr = pd.concat(
            [
                high_low,
                high_close,
                low_close
            ],
            axis=1
        ).max(axis=1)

        return tr.rolling(period).mean()

    @staticmethod
    def body(df):

        return (df["close"] - df["open"]).abs()

    @staticmethod
    def upper_wick(df):

        return df["high"] - df[["open", "close"]].max(axis=1)

    @staticmethod
    def lower_wick(df):

        return df[["open", "close"]].min(axis=1) - df["low"]

    @staticmethod
    def bullish(df):

        return df["close"] > df["open"]

    @staticmethod
    def bearish(df):

        return df["close"] < df["open"]
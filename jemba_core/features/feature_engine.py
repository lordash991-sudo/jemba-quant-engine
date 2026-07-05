import pandas as pd

from jemba_core.events.event_bus import EventBus
from jemba_core.events.feature_generated_event import FeatureGeneratedEvent


class FeatureEngine:

    _bus = EventBus()

    @staticmethod
    def ema(df, period):
        return df["close"].ewm(span=period, adjust=False).mean()

    @staticmethod
    def sma(df, column, period):
        return df[column].rolling(period).mean()

    @staticmethod
    def atr(df, period=14):
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    @staticmethod
    def body(df):
        return (df["close"] - df["open"]).abs()

    @staticmethod
    def bullish(df):
        return (df["close"] > df["open"]).astype(int)

    @staticmethod
    def bearish(df):
        return (df["close"] < df["open"]).astype(int)

    @staticmethod
    def rsi(df, period=14):
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def roc(df, period=12):
        return df["close"].pct_change(period)

    @staticmethod
    def volume_sma(df, period=20):
        return df["volume"].rolling(period).mean()

    @staticmethod
    def volume_ratio(df, period=20):
        return df["volume"] / FeatureEngine.volume_sma(df, period)

    @staticmethod
    def high_20(df):
        return df["high"].rolling(20).max()

    @staticmethod
    def low_20(df):
        return df["low"].rolling(20).min()

    @staticmethod
    def distance_high_20(df):
        return (FeatureEngine.high_20(df) - df["close"]) / df["close"]

    @staticmethod
    def distance_low_20(df):
        return (df["close"] - FeatureEngine.low_20(df)) / df["close"]

    @staticmethod
    def ema_distance(df, period):
        ema = FeatureEngine.ema(df, period)
        return (df["close"] - ema) / df["close"]

    @staticmethod
    def atr_percent(df):
        return FeatureEngine.atr(df) / df["close"]

    @staticmethod
    def range_percent(df):
        return (df["high"] - df["low"]) / df["close"]

    @staticmethod
    def accumulation_high(df, period=40):
        return df["high"].rolling(period).max()

    @staticmethod
    def accumulation_low(df, period=40):
        return df["low"].rolling(period).min()

    @staticmethod
    def accumulation_range(df, period=40):
        return FeatureEngine.accumulation_high(df, period) - FeatureEngine.accumulation_low(df, period)

    @staticmethod
    def distance_to_acc_high(df, period=40):
        return FeatureEngine.accumulation_high(df, period) - df["close"]

    @staticmethod
    def distance_to_acc_low(df, period=40):
        return df["close"] - FeatureEngine.accumulation_low(df, period)

    @staticmethod
    def inside_accumulation(df, period=40):
        high = FeatureEngine.accumulation_high(df, period)
        low = FeatureEngine.accumulation_low(df, period)
        return ((df["close"] <= high) & (df["close"] >= low)).astype(int)

    @staticmethod
    def generate(df):
        df = df.copy()

        df["EMA20"] = FeatureEngine.ema(df, 20)
        df["EMA50"] = FeatureEngine.ema(df, 50)
        df["EMA100"] = FeatureEngine.ema(df, 100)
        df["EMA200"] = FeatureEngine.ema(df, 200)

        df["ATR"] = FeatureEngine.atr(df)
        df["ATR_PCT"] = FeatureEngine.atr_percent(df)
        df["BODY"] = FeatureEngine.body(df)
        df["RANGE_PCT"] = FeatureEngine.range_percent(df)

        df["BULLISH"] = FeatureEngine.bullish(df)
        df["BEARISH"] = FeatureEngine.bearish(df)

        df["RSI"] = FeatureEngine.rsi(df)
        df["ROC"] = FeatureEngine.roc(df)

        df["VOL_SMA20"] = FeatureEngine.volume_sma(df)
        df["VOL_RATIO"] = FeatureEngine.volume_ratio(df)

        df["HIGH20"] = FeatureEngine.high_20(df)
        df["LOW20"] = FeatureEngine.low_20(df)
        df["DIST_HIGH20"] = FeatureEngine.distance_high_20(df)
        df["DIST_LOW20"] = FeatureEngine.distance_low_20(df)

        df["DIST_EMA20"] = FeatureEngine.ema_distance(df, 20)
        df["DIST_EMA50"] = FeatureEngine.ema_distance(df, 50)
        df["DIST_EMA200"] = FeatureEngine.ema_distance(df, 200)

        df["ACC_HIGH"] = FeatureEngine.accumulation_high(df)
        df["ACC_LOW"] = FeatureEngine.accumulation_low(df)
        df["ACC_RANGE"] = FeatureEngine.accumulation_range(df)
        df["DIST_ACC_HIGH"] = FeatureEngine.distance_to_acc_high(df)
        df["DIST_ACC_LOW"] = FeatureEngine.distance_to_acc_low(df)
        df["INSIDE_ACC"] = FeatureEngine.inside_accumulation(df)

        df["EMA20_GT_EMA50"] = (df["EMA20"] > df["EMA50"]).astype(int)
        df["EMA50_GT_EMA200"] = (df["EMA50"] > df["EMA200"]).astype(int)

        FeatureEngine._bus.publish(
            FeatureGeneratedEvent(
                source="FeatureEngine",
                symbol=df.attrs.get("symbol", "UNKNOWN"),
                timeframe=df.attrs.get("timeframe", "UNKNOWN"),
                rows=len(df),
                columns=len(df.columns),
                last_close=float(df.iloc[-1]["close"]),
            )
        )

        return df

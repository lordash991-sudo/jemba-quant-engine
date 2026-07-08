import pandas as pd


class FeatureEngineering:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        data["return"] = data["close"].pct_change()
        data["range"] = data["high"] - data["low"]
        data["body"] = (data["close"] - data["open"]).abs()
        data["body_ratio"] = data["body"] / data["range"].replace(0, pd.NA)

        data["ema_20"] = data["close"].ewm(span=20, adjust=False).mean()
        data["ema_50"] = data["close"].ewm(span=50, adjust=False).mean()
        data["ema_200"] = data["close"].ewm(span=200, adjust=False).mean()

        data["distance_ema_20"] = (data["close"] - data["ema_20"]) / data["close"]
        data["distance_ema_50"] = (data["close"] - data["ema_50"]) / data["close"]
        data["distance_ema_200"] = (data["close"] - data["ema_200"]) / data["close"]

        data["volatility_20"] = data["return"].rolling(20).std()
        data["momentum_10"] = data["close"].pct_change(10)

        data["tr"] = data[["high", "low", "close"]].max(axis=1) - data[
            ["high", "low", "close"]
        ].min(axis=1)
        data["atr_14"] = data["tr"].rolling(14).mean()

        return data.dropna().reset_index(drop=True)

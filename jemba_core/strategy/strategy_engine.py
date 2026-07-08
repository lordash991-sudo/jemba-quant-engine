from jemba_core.ai.predictor import Predictor
from jemba_core.features.feature_engine import FeatureEngine


class StrategyEngine:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

    def __init__(self):
        self.predictor = Predictor()

    def signal(self, df):
        df = df.copy()

        df["EMA20"] = FeatureEngine.ema(df, 20)
        df["EMA50"] = FeatureEngine.ema(df, 50)
        df["ATR"] = FeatureEngine.atr(df)
        df["BODY"] = FeatureEngine.body(df)
        df["BULLISH"] = FeatureEngine.bullish(df)
        df["BEARISH"] = FeatureEngine.bearish(df)

        prediction = self.predictor.predict_last(df)
        last = df.iloc[-1]

        if self.buy(last, prediction):
            return self.BUY

        if self.sell(last, prediction):
            return self.SELL

        return self.HOLD

    def buy(self, row, prediction):
        return (
            row["EMA20"] > row["EMA50"]
            and prediction == 1
            and row["BODY"] > row["ATR"] * 0.30
            and row["BULLISH"]
        )

    def sell(self, row, prediction):
        return (
            row["EMA20"] < row["EMA50"]
            and prediction == -1
            and row["BODY"] > row["ATR"] * 0.30
            and row["BEARISH"]
        )

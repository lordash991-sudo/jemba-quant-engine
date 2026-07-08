from __future__ import annotations

import joblib
import pandas as pd


class PredictorEngine:
    def __init__(self, model=None):
        self.model = model

    def load(self, path):
        self.model = joblib.load(path)
        return self.model

    def predict(self, df: pd.DataFrame):
        if self.model is None:
            return df

        features = df.select_dtypes(include="number").fillna(0)

        prediction = self.model.predict(features)
        probability = pd.DataFrame(self.model.predict_proba(features))

        result = df.copy()

        result["prediction"] = prediction
        result["probability_short"] = probability.iloc[:, 0].values
        result["probability_long"] = probability.iloc[:, 1].values

        return result

    def latest(self, df):
        result = self.predict(df)

        if result.empty:
            return None

        return result.iloc[-1].to_dict()

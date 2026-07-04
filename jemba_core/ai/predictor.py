from pathlib import Path
import joblib
import pandas as pd

from jemba_core.ai.feature_selector import FEATURES
from jemba_core.features.feature_engine import FeatureEngine


class Predictor:

    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict(self, df):

        df = FeatureEngine.generate(df)

        df = df.dropna()

        last = df.iloc[[-1]]

        X = last[FEATURES]

        prediction = int(self.model.predict(X)[0])

        probabilities = self.model.predict_proba(X)[0]

        sell_probability = float(probabilities[0])

        buy_probability = float(probabilities[1])

        confidence = max(buy_probability, sell_probability)

        return {
            "prediction": prediction,
            "buy_probability": buy_probability,
            "sell_probability": sell_probability,
            "confidence": confidence
        }

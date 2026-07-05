import joblib
import pandas as pd
from pathlib import Path


class Predictor:

    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self.model = joblib.load(self.model_path)

    def predict(self, features: pd.DataFrame):

        probabilities = self.model.predict_proba(features)[0]

        prediction = self.model.predict(features)[0]

        return {
            "prediction": int(prediction),
            "buy_probability": float(probabilities[1]),
            "sell_probability": float(probabilities[0]),
        }

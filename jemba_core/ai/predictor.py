from pathlib import Path
import joblib
import pandas as pd


class Predictor:

    def __init__(self):
        model_file = Path("models/trained/random_forest.pkl")

        if not model_file.exists():
            raise FileNotFoundError(
                f"No existe el modelo: {model_file}"
            )

        self.model = joblib.load(model_file)

    def predict(self, df: pd.DataFrame):
        features = [
            "EMA20",
            "EMA50",
            "ATR",
            "BODY",
            "BULLISH",
            "BEARISH",
        ]

        x = df[features]

        return self.model.predict(x)

    def predict_last(self, df):
        return self.predict(df)[-1]

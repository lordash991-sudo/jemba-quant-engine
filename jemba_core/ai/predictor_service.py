from pathlib import Path

from jemba_core.ai.predictor import Predictor
from jemba_core.events.prediction_event import PredictionEvent


class PredictorService:

    def __init__(self, model_dir="models/trained"):
        self.model_dir = Path(model_dir)
        self.predictors = {}

    def _model_path(self, symbol: str):
        clean_symbol = symbol.replace("-", "")
        return self.model_dir / f"{clean_symbol}_random_forest.pkl"

    def get_predictor(self, symbol: str):
        if symbol not in self.predictors:
            self.predictors[symbol] = Predictor(self._model_path(symbol))

        return self.predictors[symbol]

    def predict(self, symbol: str, timeframe: str, features):
        predictor = self.get_predictor(symbol)
        result = predictor.predict(features)

        buy_probability = result["buy_probability"]
        sell_probability = result["sell_probability"]

        if buy_probability >= sell_probability:
            action = "BUY"
            confidence = buy_probability
            probability = buy_probability
        else:
            action = "SELL"
            confidence = sell_probability
            probability = sell_probability

        return PredictionEvent(
            source="PredictorService",
            symbol=symbol,
            timeframe=timeframe,
            action=action,
            confidence=confidence,
            probability=probability,
            model="RandomForest",
            metadata={
                "buy_probability": buy_probability,
                "sell_probability": sell_probability,
                "raw_prediction": result["prediction"],
            },
        )

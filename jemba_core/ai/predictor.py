from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Prediction:
    symbol: str
    score: float
    direction: str
    confidence: float


class Predictor:
    def __init__(self, model: Any | None = None):
        self.model = model

    def predict(self, features: Any, symbol: str = "UNKNOWN") -> Prediction:
        if self.model is None:
            return Prediction(
                symbol=symbol,
                score=0.0,
                direction="NEUTRAL",
                confidence=0.0,
            )

        if hasattr(self.model, "predict_proba"):
            probability = self.model.predict_proba([features])[0][1]
        else:
            prediction = self.model.predict([features])[0]
            probability = float(prediction)

        direction = "LONG" if probability >= 0.5 else "SHORT"
        confidence = abs(probability - 0.5) * 2

        return Prediction(
            symbol=symbol,
            score=probability,
            direction=direction,
            confidence=confidence,
        )

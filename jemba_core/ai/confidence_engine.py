from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConfidenceResult:
    confidence: float
    probability: float
    prediction: int


class ConfidenceEngine:

    def __init__(self, min_probability: float = 0.55):
        self.min_probability = min_probability

    def calculate(self, prediction: int, probability: float) -> ConfidenceResult:
        probability = float(probability)

        if probability < self.min_probability:
            confidence = 0.0
        else:
            confidence = (
                (probability - self.min_probability)
                / (1 - self.min_probability)
            ) * 100

        confidence = max(0.0, min(100.0, confidence))

        return ConfidenceResult(
            confidence=confidence,
            probability=probability,
            prediction=prediction,
        )

    def evaluate(self, data):
        return data

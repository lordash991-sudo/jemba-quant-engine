from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass
class ConfidenceResult:
    signal: str = "NO_TRADE"
    confidence: float = 0.0
    probability: float = 0.0
    prediction: str = "NO_TRADE"
    should_trade: bool = False


class ConfidenceEngine:
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

    def calculate(
        self,
        probabilities: list[float],
        signal: str = "BUY",
    ) -> ConfidenceResult:
        if not probabilities:
            return ConfidenceResult()

        probability = float(mean(probabilities))
        final_signal = signal if probability >= self.threshold else "NO_TRADE"

        return ConfidenceResult(
            signal=final_signal,
            confidence=probability,
            probability=probability,
            prediction=final_signal,
            should_trade=probability >= self.threshold,
        )

    def evaluate(
        self,
        probabilities: list[float],
        signal: str = "BUY",
    ) -> ConfidenceResult:
        return self.calculate(probabilities, signal)

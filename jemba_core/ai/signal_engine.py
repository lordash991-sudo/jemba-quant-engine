from __future__ import annotations

from dataclasses import dataclass

from jemba_core.ai.confidence_engine import ConfidenceResult


@dataclass(slots=True)
class SignalResult:
    action: str
    confidence: float
    prediction: int
    probability: float


class SignalEngine:

    def __init__(self, min_confidence: float = 60.0):
        self.min_confidence = min_confidence

    def generate(
        self,
        confidence: ConfidenceResult,
    ) -> SignalResult:

        if confidence.confidence < self.min_confidence:
            action = "HOLD"

        elif confidence.prediction == 1:
            action = "BUY"

        elif confidence.prediction == -1:
            action = "SELL"

        else:
            action = "HOLD"

        return SignalResult(
            action=action,
            confidence=confidence.confidence,
            prediction=confidence.prediction,
            probability=confidence.probability,
        )

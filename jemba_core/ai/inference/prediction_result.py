from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PredictionResult:
    signal: int
    probability: float | None
    confidence: float | None
    model_id: str
    model_name: str
    status: str
    quality_score: float | None
    metrics: dict[str, Any]
    metadata: dict[str, Any]

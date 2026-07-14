from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SearchResult:
    best_estimator: Any
    best_params: dict[str, Any]
    best_score: float
    cv_results: dict[str, Any]
    strategy: str
    cv_strategy: str
    scoring: str | None

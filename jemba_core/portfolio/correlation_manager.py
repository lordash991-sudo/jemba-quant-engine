from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CorrelationResult:
    allowed: bool
    correlation: float
    reason: str | None = None


class CorrelationManager:
    """Block new positions with excessive absolute correlation."""

    def __init__(self, max_correlation: float = 0.80) -> None:
        if not math.isfinite(max_correlation):
            raise ValueError("MAX_CORRELATION_MUST_BE_FINITE")

        if not 0.0 <= max_correlation <= 1.0:
            raise ValueError("MAX_CORRELATION_MUST_BE_BETWEEN_0_AND_1")

        self.max_correlation = float(max_correlation)

    def check(
        self,
        correlation: float,
        *,
        same_direction: bool = True,
    ) -> CorrelationResult:
        if not math.isfinite(correlation):
            raise ValueError("CORRELATION_MUST_BE_FINITE")

        if not -1.0 <= correlation <= 1.0:
            raise ValueError("CORRELATION_MUST_BE_BETWEEN_MINUS_1_AND_1")

        if not isinstance(same_direction, bool):
            raise TypeError("SAME_DIRECTION_MUST_BE_BOOLEAN")

        effective_correlation = (
            abs(float(correlation)) if same_direction else max(0.0, float(correlation))
        )

        if effective_correlation > self.max_correlation:
            return CorrelationResult(
                allowed=False,
                correlation=float(correlation),
                reason="CORRELATION_LIMIT_REACHED",
            )

        return CorrelationResult(
            allowed=True,
            correlation=float(correlation),
        )

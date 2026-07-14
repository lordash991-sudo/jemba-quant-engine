from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def sortino_ratio(
    returns: Iterable[float],
    *,
    target_return: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    values = _validated_returns(returns)

    if periods_per_year <= 0:
        raise ValueError("PERIODS_PER_YEAR_MUST_BE_POSITIVE")

    if not np.isfinite(target_return):
        raise ValueError("TARGET_RETURN_MUST_BE_FINITE")

    if values.size == 0:
        return 0.0

    periodic_target = target_return / periods_per_year
    excess = values - periodic_target
    downside = np.minimum(excess, 0.0)
    downside_deviation = float(np.sqrt(np.mean(np.square(downside))))

    if downside_deviation == 0.0:
        return 0.0

    return float(
        np.sqrt(periods_per_year) * float(np.mean(excess)) / downside_deviation
    )


def _validated_returns(
    returns: Iterable[float],
) -> np.ndarray:
    values = np.asarray(list(returns), dtype=float)

    if values.ndim != 1:
        raise ValueError("RETURNS_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(values).all():
        raise ValueError("RETURNS_MUST_BE_FINITE")

    return values

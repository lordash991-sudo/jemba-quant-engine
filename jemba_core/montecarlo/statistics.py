from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray


def validated_values(
    values: Iterable[float],
) -> NDArray[np.float64]:
    array = np.asarray(list(values), dtype=float)

    if array.ndim != 1:
        raise ValueError("VALUES_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(array).all():
        raise ValueError("VALUES_MUST_BE_FINITE")

    return array


def mean(values: Iterable[float]) -> float:
    array = validated_values(values)

    if array.size == 0:
        return 0.0

    return float(np.mean(array))


def median(values: Iterable[float]) -> float:
    array = validated_values(values)

    if array.size == 0:
        return 0.0

    return float(np.median(array))


def standard_deviation(
    values: Iterable[float],
) -> float:
    array = validated_values(values)

    if array.size < 2:
        return 0.0

    return float(np.std(array, ddof=1))


def percentile(
    values: Iterable[float],
    level: float,
) -> float:
    array = validated_values(values)

    if not 0.0 <= level <= 100.0:
        raise ValueError("PERCENTILE_MUST_BE_BETWEEN_0_AND_100")

    if array.size == 0:
        return 0.0

    return float(np.percentile(array, level))


def confidence_interval(
    values: Iterable[float],
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    array = validated_values(values)

    if not 0.0 < confidence < 1.0:
        raise ValueError("CONFIDENCE_MUST_BE_BETWEEN_0_AND_1")

    if array.size == 0:
        return 0.0, 0.0

    tail = (1.0 - confidence) / 2.0

    lower = float(np.quantile(array, tail))
    upper = float(np.quantile(array, 1.0 - tail))

    return lower, upper

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray


def drawdown_series(
    equity: Iterable[float],
) -> NDArray[np.float64]:
    values = np.asarray(list(equity), dtype=float)

    if values.ndim != 1:
        raise ValueError("EQUITY_MUST_BE_ONE_DIMENSIONAL")

    if values.size == 0:
        return np.array([], dtype=float)

    if not np.isfinite(values).all():
        raise ValueError("EQUITY_MUST_BE_FINITE")

    peaks = np.maximum.accumulate(values)

    return np.divide(
        values - peaks,
        peaks,
        out=np.zeros_like(values, dtype=float),
        where=peaks != 0,
    )


def max_drawdown(
    equity: Iterable[float],
) -> float:
    drawdowns = drawdown_series(equity)

    if drawdowns.size == 0:
        return 0.0

    return float(abs(np.min(drawdowns)))


def average_drawdown(
    equity: Iterable[float],
) -> float:
    drawdowns = drawdown_series(equity)
    negative = drawdowns[drawdowns < 0]

    if negative.size == 0:
        return 0.0

    return float(abs(np.mean(negative)))

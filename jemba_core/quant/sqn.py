from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def sqn(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)

    if values.size < 2:
        return 0.0

    deviation = float(np.std(values, ddof=1))

    if deviation == 0.0:
        return 0.0

    return float(np.sqrt(values.size) * float(np.mean(values)) / deviation)


def _validated_trades(
    trades: Iterable[float],
) -> np.ndarray:
    values = np.asarray(list(trades), dtype=float)

    if values.ndim != 1:
        raise ValueError("TRADES_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(values).all():
        raise ValueError("TRADES_MUST_BE_FINITE")

    return values

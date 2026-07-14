from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def gross_profit(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)

    return float(values[values > 0].sum())


def gross_loss(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)

    return float(abs(values[values < 0].sum()))


def profit_factor(
    trades: Iterable[float],
) -> float:
    profit = gross_profit(trades)
    loss = gross_loss(trades)

    if loss == 0.0:
        if profit > 0.0:
            return float("inf")

        return 0.0

    return float(profit / loss)


def _validated_trades(
    trades: Iterable[float],
) -> np.ndarray:
    values = np.asarray(list(trades), dtype=float)

    if values.ndim != 1:
        raise ValueError("TRADES_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(values).all():
        raise ValueError("TRADES_MUST_BE_FINITE")

    return values

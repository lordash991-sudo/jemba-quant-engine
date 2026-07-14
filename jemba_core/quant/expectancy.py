from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def win_rate(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)

    if values.size == 0:
        return 0.0

    return float(np.mean(values > 0))


def loss_rate(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)

    if values.size == 0:
        return 0.0

    return float(np.mean(values < 0))


def average_win(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)
    winners = values[values > 0]

    if winners.size == 0:
        return 0.0

    return float(np.mean(winners))


def average_loss(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)
    losers = values[values < 0]

    if losers.size == 0:
        return 0.0

    return float(abs(np.mean(losers)))


def expectancy(
    trades: Iterable[float],
) -> float:
    values = _validated_trades(trades)

    if values.size == 0:
        return 0.0

    return float(
        win_rate(values) * average_win(values)
        - loss_rate(values) * average_loss(values)
    )


def _validated_trades(
    trades: Iterable[float],
) -> np.ndarray:
    values = np.asarray(list(trades), dtype=float)

    if values.ndim != 1:
        raise ValueError("TRADES_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(values).all():
        raise ValueError("TRADES_MUST_BE_FINITE")

    return values

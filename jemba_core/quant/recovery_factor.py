from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from jemba_core.quant.drawdown import max_drawdown


def recovery_factor(
    equity: Iterable[float],
) -> float:
    values = _validated_equity(equity)

    if values.size < 2:
        return 0.0

    initial = float(values[0])
    final = float(values[-1])
    net_profit = final - initial
    drawdown_fraction = max_drawdown(values)

    if drawdown_fraction == 0.0:
        if net_profit > 0.0:
            return float("inf")

        return 0.0

    drawdown_amount = drawdown_fraction * float(np.max(values))

    if drawdown_amount == 0.0:
        return 0.0

    return float(net_profit / drawdown_amount)


def _validated_equity(
    equity: Iterable[float],
) -> np.ndarray:
    values = np.asarray(list(equity), dtype=float)

    if values.ndim != 1:
        raise ValueError("EQUITY_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(values).all():
        raise ValueError("EQUITY_MUST_BE_FINITE")

    return values

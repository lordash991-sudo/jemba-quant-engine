from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from jemba_core.quant.drawdown import max_drawdown


def annualized_return(
    equity: Iterable[float],
    *,
    periods_per_year: int = 252,
) -> float:
    values = _validated_equity(equity)

    if periods_per_year <= 0:
        raise ValueError("PERIODS_PER_YEAR_MUST_BE_POSITIVE")

    if values.size < 2:
        return 0.0

    initial = float(values[0])
    final = float(values[-1])

    if initial <= 0.0 or final <= 0.0:
        return 0.0

    periods = values.size - 1

    return float((final / initial) ** (periods_per_year / periods) - 1.0)


def calmar_ratio(
    equity: Iterable[float],
    *,
    periods_per_year: int = 252,
) -> float:
    values = _validated_equity(equity)
    drawdown = max_drawdown(values)

    if drawdown == 0.0:
        return 0.0

    return float(
        annualized_return(
            values,
            periods_per_year=periods_per_year,
        )
        / drawdown
    )


def _validated_equity(
    equity: Iterable[float],
) -> np.ndarray:
    values = np.asarray(list(equity), dtype=float)

    if values.ndim != 1:
        raise ValueError("EQUITY_MUST_BE_ONE_DIMENSIONAL")

    if not np.isfinite(values).all():
        raise ValueError("EQUITY_MUST_BE_FINITE")

    return values

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from jemba_core.quant.drawdown import max_drawdown


@dataclass(frozen=True, slots=True)
class Simulation:
    trades: NDArray[np.float64]
    equity_curve: NDArray[np.float64]
    final_equity: float
    net_profit: float
    max_drawdown: float

    @classmethod
    def from_trades(
        cls,
        trades: NDArray[np.float64],
        *,
        initial_balance: float,
    ) -> Simulation:
        values = np.asarray(trades, dtype=float)

        if values.ndim != 1:
            raise ValueError("TRADES_MUST_BE_ONE_DIMENSIONAL")

        if not np.isfinite(values).all():
            raise ValueError("TRADES_MUST_BE_FINITE")

        if not np.isfinite(initial_balance):
            raise ValueError("INITIAL_BALANCE_MUST_BE_FINITE")

        cumulative = np.cumsum(values, dtype=float)

        equity_curve = np.concatenate(
            (
                np.array([float(initial_balance)]),
                float(initial_balance) + cumulative,
            )
        )

        return cls(
            trades=values.copy(),
            equity_curve=equity_curve,
            final_equity=float(equity_curve[-1]),
            net_profit=float(values.sum()),
            max_drawdown=max_drawdown(equity_curve),
        )

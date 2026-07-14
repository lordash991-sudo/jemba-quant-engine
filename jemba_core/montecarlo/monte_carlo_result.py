from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class MonteCarloResult:
    simulations: int
    initial_balance: float
    mean_final_equity: float
    median_final_equity: float
    standard_deviation: float
    best_case: float
    worst_case: float
    percentile_5: float
    percentile_95: float
    confidence_interval_95: tuple[float, float]
    mean_max_drawdown: float
    worst_max_drawdown: float
    final_equities: NDArray[np.float64]
    max_drawdowns: NDArray[np.float64]
    equity_curves: NDArray[np.float64]

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulations": self.simulations,
            "initial_balance": self.initial_balance,
            "mean_final_equity": self.mean_final_equity,
            "median_final_equity": self.median_final_equity,
            "standard_deviation": self.standard_deviation,
            "best_case": self.best_case,
            "worst_case": self.worst_case,
            "percentile_5": self.percentile_5,
            "percentile_95": self.percentile_95,
            "confidence_interval_95": list(self.confidence_interval_95),
            "mean_max_drawdown": self.mean_max_drawdown,
            "worst_max_drawdown": self.worst_max_drawdown,
            "final_equities": self.final_equities.tolist(),
            "max_drawdowns": self.max_drawdowns.tolist(),
            "equity_curves": self.equity_curves.tolist(),
        }

    @property
    def mean_net_profit(self) -> float:
        return float(self.mean_final_equity - self.initial_balance)

    @property
    def worst_net_profit(self) -> float:
        return float(self.worst_case - self.initial_balance)

    @property
    def best_net_profit(self) -> float:
        return float(self.best_case - self.initial_balance)

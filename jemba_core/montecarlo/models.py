from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MonteCarloResult:
    simulations: int
    initial_balance: float
    mean_final_balance: float
    worst_final_balance: float
    best_final_balance: float
    mean_max_drawdown: float
    worst_max_drawdown: float
    risk_of_ruin: float

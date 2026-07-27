from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BacktestMetrics:
    symbol: str
    timeframe: str
    initial_capital: float
    final_capital: float
    net_profit: float
    total_return_pct: float
    total_trades: int
    wins: int
    losses: int
    breakeven: int
    win_rate: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    expectancy: float
    average_win: float
    average_loss: float
    best_trade: float
    worst_trade: float
    max_drawdown_pct: float
    recovery_factor: float
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
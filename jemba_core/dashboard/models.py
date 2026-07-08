from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DashboardSnapshot:
    balance: float
    equity: float
    pnl_today: float
    drawdown: float
    open_positions: int
    current_regime: str
    regime_confidence: float
    ai_confidence: float
    risk_of_ruin: float
    system_status: str

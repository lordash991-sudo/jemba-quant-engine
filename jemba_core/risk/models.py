from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RiskRequest:
    symbol: str
    side: str
    entry_price: float
    stop_loss_price: float
    confidence: float
    account_balance: float
    open_positions: int = 0


@dataclass(slots=True)
class RiskDecision:
    approved: bool
    reason: str
    risk_percent: float = 0.0
    position_size: float = 0.0
    max_loss: float = 0.0

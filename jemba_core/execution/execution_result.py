from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    approved: bool
    symbol: str

    entry_price: float
    executed_price: float
    quantity: float

    notional: float
    margin_used: float

    commission: float
    slippage: float

    order_id: str | None
    timestamp: datetime
    reason: str | None = None

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class VolatilityRegime(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    symbol: str
    side: OrderSide
    order_type: OrderType

    entry_price: float
    quantity: float
    leverage: int
    risk_percent: float

    stop_loss: float
    take_profit: float

    available_margin: float
    volatility: VolatilityRegime = VolatilityRegime.MEDIUM

    decision_approved: bool = True
    market_open: bool = True
    kill_switch: bool = False
    duplicate_position: bool = False
    portfolio_approved: bool = True
    exposure_approved: bool = True
    correlation_approved: bool = True

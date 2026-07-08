from dataclasses import dataclass


@dataclass(slots=True)
class Trade:
    symbol: str
    side: str
    entry: float
    exit: float
    quantity: float
    pnl: float
    pnl_percent: float
    commission: float = 0.0

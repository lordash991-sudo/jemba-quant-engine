from dataclasses import dataclass


@dataclass
class PaperPosition:
    symbol: str
    action: str
    entry: float
    quantity: float
    stop_loss: float
    take_profit: float
    status: str = "OPEN"
    pnl: float = 0.0

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaperPosition:

    symbol: str

    side: str

    entry: float

    stop_loss: float

    take_profit: float

    quantity: float

    confidence: float

    opened_at: datetime

    status: str = "OPEN"

    exit_price: float = 0.0

    pnl: float = 0.0

    commission: float = 0.0

    closed_at: datetime | None = None

    def close(self, exit_price: float, commission: float = 0.0):

        self.exit_price = exit_price

        self.commission = commission

        self.closed_at = datetime.utcnow()

        self.status = "CLOSED"

        if self.side == "BUY":

            self.pnl = (
                (exit_price - self.entry)
                * self.quantity
                - commission
            )

        else:

            self.pnl = (
                (self.entry - exit_price)
                * self.quantity
                - commission
            )

        return self.pnl

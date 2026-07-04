from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:

    symbol: str
    side: str
    entry: float
    stop_loss: float
    take_profit: float
    quantity: float
    confidence: float
    opened_at: datetime
    status: str = "OPEN"


class TradeEngine:

    def __init__(self, portfolio):

        self.portfolio = portfolio
        self.current_trade = None

    def can_open_trade(self):

        return (
            self.current_trade is None
            and self.portfolio.can_open_position()
        )

    def create_trade(
        self,
        symbol,
        side,
        entry,
        stop_loss,
        take_profit,
        confidence
    ):

        if not self.can_open_trade():
            return None

        quantity = self.portfolio.calculate_position_size(
            entry,
            stop_loss
        )

        trade = Trade(
            symbol=symbol,
            side=side,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity,
            confidence=confidence,
            opened_at=datetime.utcnow()
        )

        self.current_trade = trade

        self.portfolio.register_position(
            {
                "symbol": symbol,
                "side": side
            }
        )

        return trade

    def close_trade(self, pnl):

        if self.current_trade is None:
            return

        self.current_trade.status = "CLOSED"

        self.portfolio.close_position(pnl)

        self.current_trade = None

    def summary(self):

        if self.current_trade is None:
            return {
                "status": "NO_POSITION"
            }

        return vars(self.current_trade)

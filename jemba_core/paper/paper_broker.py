from __future__ import annotations

from dataclasses import dataclass

from jemba_core.paper.paper_account import PaperAccount


@dataclass(slots=True)
class PaperOrder:
    symbol: str
    side: str
    size: float
    price: float
    status: str = "FILLED"


@dataclass(slots=True)
class PaperPosition:
    symbol: str
    side: str
    size: float
    entry_price: float


class PaperBroker:

    def __init__(self, account: PaperAccount | None = None):
        self.account = account or PaperAccount()
        self.positions = {}

    def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float = 0.0,
    ) -> PaperOrder:

        if size <= 0:
            return PaperOrder(symbol, side, size, price, status="REJECTED")

        reserved = self.account.reserve_margin(size)

        if not reserved:
            return PaperOrder(symbol, side, size, price, status="REJECTED")

        self.positions[symbol] = PaperPosition(
            symbol=symbol,
            side=side,
            size=size,
            entry_price=price,
        )

        return PaperOrder(symbol, side, size, price, status="FILLED")

    def get_position(self, symbol: str):
        return self.positions.get(symbol)

    def close_position(self, symbol: str):
        position = self.positions.pop(symbol, None)

        if position is None:
            return None

        self.account.release_margin(position.size)

        return position

    def balance(self):
        return self.account.balance

    def equity(self):
        return self.account.equity

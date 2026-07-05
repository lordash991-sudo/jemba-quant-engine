from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderResult:
    success: bool
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: datetime
    message: str = ""


class OrderExecutor:

    def __init__(self, provider=None):
        self.provider = provider

    def market_buy(self, symbol, quantity):

        print(f"[BUY] {symbol} qty={quantity}")

        return OrderResult(
            success=True,
            order_id=f"BUY-{int(datetime.utcnow().timestamp())}",
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            price=0,
            timestamp=datetime.utcnow()
        )

    def market_sell(self, symbol, quantity):

        print(f"[SELL] {symbol} qty={quantity}")

        return OrderResult(
            success=True,
            order_id=f"SELL-{int(datetime.utcnow().timestamp())}",
            symbol=symbol,
            side="SELL",
            quantity=quantity,
            price=0,
            timestamp=datetime.utcnow()
        )

    def close_position(self, symbol):

        print(f"[CLOSE] {symbol}")

        return True

    def cancel_order(self, order_id):

        print(f"[CANCEL] {order_id}")

        return True

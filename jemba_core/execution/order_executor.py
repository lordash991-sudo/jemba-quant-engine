from __future__ import annotations


class OrderExecutor:
    def __init__(self, broker, storage=None):
        self.broker = broker
        self.storage = storage

    def execute(self, trade):
        result = self.broker.place_order(
            symbol=trade.symbol,
            side=trade.side,
            size=trade.size,
        )

        if self.storage is not None:
            self.storage.create_tables()
            self.storage.insert_trade(
                symbol=trade.symbol,
                side=trade.side,
                size=trade.size,
                entry=0,
                exit_price=0,
                pnl=0,
            )

        return result

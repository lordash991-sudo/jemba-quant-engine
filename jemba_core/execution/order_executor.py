from __future__ import annotations


class OrderExecutor:

    def __init__(self, broker):
        self.broker = broker

    def execute(self, trade):

        return self.broker.place_order(
            symbol=trade.symbol,
            side=trade.side,
            size=trade.size,
        )
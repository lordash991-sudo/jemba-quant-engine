from __future__ import annotations


class PaperEngine:

    def __init__(
        self,
        trade_engine,
        order_executor,
    ):
        self.trade_engine = trade_engine
        self.order_executor = order_executor

    def run_once(self, candles, symbol="BTCUSDT"):
        trade = self.trade_engine.execute(
            candles=candles,
            symbol=symbol,
        )

        if trade is None:
            return None

        return self.order_executor.execute(trade)

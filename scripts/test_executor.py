import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.execution.order_executor import OrderExecutor


class FakeProvider:
    def place_market_order(self, symbol, side, quantity, stop_loss, take_profit):
        print()
        print("===== ORDEN SIMULADA =====")
        print(symbol)
        print(side)
        print(quantity)
        print(stop_loss)
        print(take_profit)

        return {"orderId": "TEST-123456"}


class Signal:
    symbol = "BTC-USDT"
    action = "BUY"
    quantity = 0.01
    stop_loss = 61500
    take_profit = 64500


executor = OrderExecutor(FakeProvider())
result = executor.execute(Signal())

print()
print(result)

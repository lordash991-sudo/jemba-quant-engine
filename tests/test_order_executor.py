from unittest.mock import MagicMock

from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.execution.order_executor import OrderExecutor


class Trade:
    symbol = "BTCUSDT"
    side = "LONG"
    size = 0.25


def test_execute_order():
    broker = MagicMock()

    broker.place_order.return_value = {
        "status": "FILLED"
    }

    executor = OrderExecutor(broker)

    result = executor.execute(Trade())

    broker.place_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="LONG",
        size=0.25,
    )

    assert result["status"] == "FILLED"


def test_execute_order_saves_trade(tmp_path):
    broker = MagicMock()

    broker.place_order.return_value = {
        "status": "FILLED"
    }

    storage = SQLiteStorage(tmp_path / "test.db")

    executor = OrderExecutor(
        broker=broker,
        storage=storage,
    )

    executor.execute(Trade())

    trades = storage.trades()

    assert len(trades) == 1
    assert trades[0]["symbol"] == "BTCUSDT"
    assert trades[0]["side"] == "LONG"

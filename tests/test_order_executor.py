from unittest.mock import MagicMock

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
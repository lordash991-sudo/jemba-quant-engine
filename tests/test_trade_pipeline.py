from types import SimpleNamespace
from unittest.mock import MagicMock

from jemba_core.execution.order_executor import OrderExecutor
from jemba_core.paper.paper_engine import PaperEngine


def test_trade_pipeline():
    broker = MagicMock()

    broker.place_order.return_value = {"status": "FILLED"}

    trade_engine = MagicMock()

    trade_engine.execute.return_value = SimpleNamespace(
        symbol="BTCUSDT",
        side="LONG",
        size=0.25,
    )

    executor = OrderExecutor(broker)

    paper = PaperEngine(
        trade_engine=trade_engine,
        order_executor=executor,
    )

    result = paper.run_once([])

    assert result["status"] == "FILLED"

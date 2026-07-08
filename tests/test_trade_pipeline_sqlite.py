from types import SimpleNamespace
from unittest.mock import MagicMock

from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.execution.order_executor import OrderExecutor
from jemba_core.paper.paper_engine import PaperEngine


def test_trade_pipeline_saves_to_sqlite(tmp_path):
    broker = MagicMock()

    broker.place_order.return_value = {"status": "FILLED"}

    trade_engine = MagicMock()

    trade_engine.execute.return_value = SimpleNamespace(
        symbol="BTCUSDT",
        side="LONG",
        size=0.25,
    )

    storage = SQLiteStorage(tmp_path / "test.db")

    executor = OrderExecutor(
        broker=broker,
        storage=storage,
    )

    paper = PaperEngine(
        trade_engine=trade_engine,
        order_executor=executor,
    )

    result = paper.run_once(
        candles=[],
        symbol="BTCUSDT",
    )

    trades = storage.trades()

    assert result["status"] == "FILLED"
    assert len(trades) == 1
    assert trades[0]["symbol"] == "BTCUSDT"
    assert trades[0]["side"] == "LONG"
    assert trades[0]["size"] == 0.25

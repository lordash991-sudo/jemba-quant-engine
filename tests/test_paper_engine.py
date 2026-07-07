from unittest.mock import MagicMock

from jemba_core.paper.paper_engine import PaperEngine


def test_paper_engine_run_once():
    trade_engine = MagicMock()
    order_executor = MagicMock()

    trade_engine.execute.return_value = "TRADE"
    order_executor.execute.return_value = {
        "status": "FILLED"
    }

    engine = PaperEngine(
        trade_engine=trade_engine,
        order_executor=order_executor,
    )

    result = engine.run_once(
        candles=[],
        symbol="BTCUSDT",
    )

    trade_engine.execute.assert_called_once_with(
        candles=[],
        symbol="BTCUSDT",
    )

    order_executor.execute.assert_called_once_with("TRADE")

    assert result["status"] == "FILLED"


def test_paper_engine_no_trade():
    trade_engine = MagicMock()
    order_executor = MagicMock()

    trade_engine.execute.return_value = None

    engine = PaperEngine(
        trade_engine=trade_engine,
        order_executor=order_executor,
    )

    result = engine.run_once(
        candles=[],
        symbol="BTCUSDT",
    )

    assert result is None
    order_executor.execute.assert_not_called()

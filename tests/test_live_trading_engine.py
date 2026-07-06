from unittest.mock import MagicMock

from jemba_core.engine.live_trading_engine import LiveTradingEngine


def build_engine():
    market = MagicMock()
    pipeline = MagicMock()
    execution = MagicMock()
    scheduler = MagicMock()
    scheduler.should_continue.side_effect = [True, False]

    engine = LiveTradingEngine(
        market_provider=market,
        pipeline_engine=pipeline,
        execution_engine=execution,
        scheduler=scheduler,
        symbols=["BTC-USDT", "ETH-USDT"],
    )

    return engine, market, pipeline, execution, scheduler


def test_get_candles_called():
    engine, market, pipeline, execution, scheduler = build_engine()
    market.get_candles.return_value = []
    pipeline.process.return_value = None

    engine.run_once()

    assert market.get_candles.call_count == 2


def test_pipeline_called():
    engine, market, pipeline, execution, scheduler = build_engine()
    market.get_candles.return_value = []
    pipeline.process.return_value = None

    engine.run_once()

    assert pipeline.process.call_count == 2


def test_execute_called():
    engine, market, pipeline, execution, scheduler = build_engine()
    market.get_candles.return_value = []
    pipeline.process.return_value = MagicMock()

    engine.run_once()

    assert execution.execute.call_count == 2


def test_execute_not_called():
    engine, market, pipeline, execution, scheduler = build_engine()
    market.get_candles.return_value = []
    pipeline.process.return_value = None

    engine.run_once()

    execution.execute.assert_not_called()


def test_run_calls_sleep():
    engine, market, pipeline, execution, scheduler = build_engine()
    market.get_candles.return_value = []
    pipeline.process.return_value = None

    engine.run()

    scheduler.sleep.assert_called_once()


def test_multiple_symbols():
    engine, market, pipeline, execution, scheduler = build_engine()
    market.get_candles.return_value = []
    pipeline.process.return_value = None

    engine.run_once()

    calls = [c.kwargs["symbol"] for c in market.get_candles.call_args_list]

    assert calls == ["BTC-USDT", "ETH-USDT"]

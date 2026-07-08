from unittest.mock import MagicMock

from jemba_core.paper.paper_execution_engine import PaperExecutionEngine


def test_execute_order_success():
    broker_executor = MagicMock()
    paper_engine = MagicMock()
    reporter = MagicMock()
    statistics = MagicMock()

    order = MagicMock()
    broker_executor.execute.return_value = order

    engine = PaperExecutionEngine(
        broker_executor=broker_executor,
        paper_engine=paper_engine,
        reporter=reporter,
        statistics=statistics,
    )

    result = engine.execute(MagicMock())

    assert result == order


def test_execute_returns_none_when_broker_fails():
    broker_executor = MagicMock()
    paper_engine = MagicMock()
    reporter = MagicMock()
    statistics = MagicMock()

    broker_executor.execute.return_value = None

    engine = PaperExecutionEngine(
        broker_executor=broker_executor,
        paper_engine=paper_engine,
        reporter=reporter,
        statistics=statistics,
    )

    result = engine.execute(MagicMock())

    assert result is None


def test_paper_engine_register_called():
    broker_executor = MagicMock()
    paper_engine = MagicMock()
    reporter = MagicMock()
    statistics = MagicMock()

    order = MagicMock()
    broker_executor.execute.return_value = order

    engine = PaperExecutionEngine(
        broker_executor=broker_executor,
        paper_engine=paper_engine,
        reporter=reporter,
        statistics=statistics,
    )

    engine.execute(MagicMock())

    paper_engine.register.assert_called_once_with(order)


def test_statistics_update_called():
    broker_executor = MagicMock()
    paper_engine = MagicMock()
    reporter = MagicMock()
    statistics = MagicMock()

    order = MagicMock()
    broker_executor.execute.return_value = order

    engine = PaperExecutionEngine(
        broker_executor=broker_executor,
        paper_engine=paper_engine,
        reporter=reporter,
        statistics=statistics,
    )

    engine.execute(MagicMock())

    statistics.update.assert_called_once_with(order)


def test_reporter_record_called():
    broker_executor = MagicMock()
    paper_engine = MagicMock()
    reporter = MagicMock()
    statistics = MagicMock()

    order = MagicMock()
    broker_executor.execute.return_value = order

    engine = PaperExecutionEngine(
        broker_executor=broker_executor,
        paper_engine=paper_engine,
        reporter=reporter,
        statistics=statistics,
    )

    engine.execute(MagicMock())

    reporter.record.assert_called_once_with(order)

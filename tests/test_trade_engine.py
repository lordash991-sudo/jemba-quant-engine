from unittest.mock import MagicMock

from jemba_core.execution.trade_engine import TradeEngine


def test_trade_engine():
    feature = MagicMock()
    predictor = MagicMock()
    confidence = MagicMock()
    signal = MagicMock()
    ranking = MagicMock()
    risk = MagicMock()
    portfolio = MagicMock()

    feature.latest.return_value = {}

    predictor.latest.return_value = {
        "prediction": "LONG",
        "probability_long": 0.91,
    }

    confidence.calculate.return_value = 0.91
    signal.generate.return_value = "LONG"
    ranking.rank.return_value = {}
    risk.evaluate.return_value = {}
    portfolio.allocate.return_value = 0.25

    engine = TradeEngine(
        feature,
        predictor,
        confidence,
        signal,
        ranking,
        risk,
        portfolio,
    )

    trade = engine.execute([])

    assert trade.side == "LONG"
    assert trade.size == 0.25
    assert trade.probability == 0.91

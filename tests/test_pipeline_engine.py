from unittest.mock import MagicMock

import pandas as pd

from jemba_core.engine.pipeline_engine import PipelineEngine
from jemba_core.engine.trading_opportunity import TradingOpportunity
from jemba_core.ai.confidence_engine import ConfidenceEngine
from jemba_core.signals.signal_engine import SignalEngine
from jemba_core.signals.signal_ranker import SignalRanker
from jemba_core.risk.risk_engine import RiskEngine
from jemba_core.portfolio.portfolio_manager import PortfolioManager


class FakePrediction:

    def __init__(self, action="BUY", probability=0.95):
        self.action = action
        self.probability = probability


def sample_features():
    return pd.DataFrame([
        {
            "close": 100.0,
            "ATR": 5.0,
            "ATR_PCT": 0.02,
            "RSI": 55.0,
            "EMA20": 105.0,
            "EMA50": 100.0,
        }
    ])


def build_engine():
    feature_engine = MagicMock()
    feature_engine.generate.return_value = sample_features()

    predictor = MagicMock()
    predictor.predict.return_value = FakePrediction()

    return PipelineEngine(
        feature_engine=feature_engine,
        predictor=predictor,
        confidence_engine=ConfidenceEngine(),
        signal_engine=SignalEngine(),
        ranking_engine=SignalRanker(),
        risk_engine=RiskEngine(min_confidence=0.70),
        portfolio_manager=PortfolioManager(
            account_balance=10000,
            risk_per_trade=0.01,
            max_positions=1,
        ),
    )


def test_pipeline_success():
    engine = build_engine()

    result = engine.process(
        symbol="BTC-USDT",
        timeframe="1h",
        candles=pd.DataFrame(),
    )

    assert isinstance(result, TradingOpportunity)
    assert result.symbol == "BTC-USDT"
    assert result.action == "BUY"
    assert result.approved is True
    assert result.position_size > 0


def test_pipeline_features_none():
    engine = build_engine()
    engine.feature_engine.generate.return_value = None

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_prediction_none():
    engine = build_engine()
    engine.predictor.predict.return_value = None

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_low_confidence():
    engine = build_engine()
    engine.predictor.predict.return_value = FakePrediction(probability=0.10)

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_signal_none():
    engine = build_engine()
    engine.predictor.predict.return_value = FakePrediction(action="HOLD", probability=0.95)

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_ranking_empty():
    engine = build_engine()
    engine.ranking_engine.rank = MagicMock(return_value=[])

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_risk_rejected():
    engine = build_engine()
    engine.risk_engine.validate = MagicMock(
        return_value={
            "approved": False,
            "reasons": ["TEST_REJECTED"],
        }
    )

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_portfolio_full():
    engine = build_engine()
    engine.portfolio_manager.register_position({
        "symbol": "ETH-USDT",
        "side": "BUY",
    })

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None


def test_pipeline_unexpected_exception():
    engine = build_engine()
    engine.feature_engine.generate.side_effect = Exception("boom")

    result = engine.process("BTC-USDT", "1h", pd.DataFrame())

    assert result is None

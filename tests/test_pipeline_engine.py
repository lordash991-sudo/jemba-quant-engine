from unittest.mock import MagicMock

from jemba_core.ai.predictor_engine import PredictorEngine
from jemba_core.features.feature_engine import FeatureEngine
from jemba_core.pipeline.pipeline_engine import PipelineEngine


def sample_candles():
    candles = []

    for i in range(250):
        price = 100 + i
        candles.append(
            {
                "open": str(price),
                "high": str(price + 5),
                "low": str(price - 5),
                "close": str(price + 2),
                "volume": str(1000 + i),
            }
        )

    return candles


def test_pipeline_uses_default_engines():
    pipeline = PipelineEngine()

    assert isinstance(pipeline.feature_engine, FeatureEngine)
    assert isinstance(pipeline.predictor, PredictorEngine)


def test_pipeline_generates_features_without_model():
    pipeline = PipelineEngine()

    result = pipeline.execute(sample_candles())

    assert "ema_20" in result.columns
    assert "rsi_14" in result.columns
    assert "atr_14" in result.columns


def test_pipeline_uses_predictor():
    predictor = MagicMock()
    predictor.predict.return_value = "prediction"

    pipeline = PipelineEngine(predictor=predictor)

    result = pipeline.execute(sample_candles())

    assert result == "prediction"
    predictor.predict.assert_called_once()


def test_pipeline_full_chain():
    feature = MagicMock()
    predictor = MagicMock()
    confidence = MagicMock()
    signal = MagicMock()
    ranking = MagicMock()
    risk = MagicMock()
    portfolio = MagicMock()
    execution = MagicMock()

    feature.build.return_value = "features"
    predictor.predict.return_value = "prediction"
    confidence.evaluate.return_value = "confidence"
    signal.generate.return_value = "signal"
    ranking.rank.return_value = "ranked"
    risk.apply.return_value = "risk"
    portfolio.update.return_value = "portfolio"
    execution.execute.return_value = "done"

    pipeline = PipelineEngine(
        feature_engine=feature,
        predictor=predictor,
        confidence_engine=confidence,
        signal_engine=signal,
        ranking_engine=ranking,
        risk_engine=risk,
        portfolio_manager=portfolio,
        execution_engine=execution,
    )

    result = pipeline.execute("market")

    assert result == "done"

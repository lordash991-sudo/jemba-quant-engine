from unittest.mock import MagicMock

from jemba_core.pipeline.pipeline_engine import PipelineEngine


def test_pipeline_engine():
    feature = MagicMock()
    predictor = MagicMock()
    confidence = MagicMock()
    signal = MagicMock()
    ranking = MagicMock()
    risk = MagicMock()
    portfolio = MagicMock()
    execution = MagicMock()

    feature.compute.return_value = "features"
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

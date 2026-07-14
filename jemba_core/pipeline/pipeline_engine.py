from __future__ import annotations

from typing import Any

from jemba_core.ai.predictor_engine import PredictorEngine
from jemba_core.features.feature_engine import FeatureEngine


class PipelineEngine:
    def __init__(
        self,
        feature_engine: Any | None = None,
        predictor: Any | None = None,
        confidence_engine: Any | None = None,
        signal_engine: Any | None = None,
        ranking_engine: Any | None = None,
        risk_engine: Any | None = None,
        portfolio_manager: Any | None = None,
        execution_engine: Any | None = None,
    ) -> None:
        self.feature_engine = feature_engine or FeatureEngine()
        self.predictor = predictor or PredictorEngine()
        self.confidence_engine = confidence_engine
        self.signal_engine = signal_engine
        self.ranking_engine = ranking_engine
        self.risk_engine = risk_engine
        self.portfolio_manager = portfolio_manager
        self.execution_engine = execution_engine

    def execute(
        self,
        market: Any | None = None,
    ) -> Any:
        data = market

        if self.feature_engine is not None:
            data = self.feature_engine.build(data)

        if self._predictor_is_ready():
            data = self.predictor.predict(data)

        if self.confidence_engine is not None:
            data = self.confidence_engine.evaluate(data)

        if self.signal_engine is not None:
            data = self.signal_engine.generate(data)

        if self.ranking_engine is not None:
            data = self.ranking_engine.rank(data)

        if self.risk_engine is not None:
            data = self.risk_engine.apply(data)

        if self.portfolio_manager is not None:
            data = self.portfolio_manager.update(data)

        if self.execution_engine is not None:
            data = self.execution_engine.execute(data)

        return data

    def _predictor_is_ready(self) -> bool:
        if self.predictor is None:
            return False

        is_configured = getattr(
            self.predictor,
            "is_configured",
            None,
        )

        if is_configured is None:
            return True

        return bool(is_configured)

from __future__ import annotations

from time import perf_counter
from typing import Any

import numpy as np

from jemba_core.ai.inference.feature_validator import FeatureValidator
from jemba_core.ai.inference.prediction_result import PredictionResult
from jemba_core.ai.registry_core.metadata import ModelRecord
from jemba_core.ai.registry_core.model_loader import ModelLoader


class InferenceService:
    def __init__(
        self,
        model_loader: ModelLoader,
        feature_validator: FeatureValidator,
    ) -> None:
        self.model_loader = model_loader
        self.feature_validator = feature_validator
        self._cached_model: Any | None = None
        self._cached_model_id: str | None = None

    def predict(
        self,
        features: Any,
        *,
        verify_artifact: bool = True,
    ) -> PredictionResult:
        started_at = perf_counter()

        validated = self.feature_validator.validate(features)
        record = self.model_loader.production_record()
        model, cache_hit = self._get_production_model(
            record,
            verify_artifact=verify_artifact,
        )

        if not hasattr(model, "predict"):
            raise TypeError("MODEL_DOES_NOT_SUPPORT_PREDICT")

        raw_prediction = model.predict(validated)
        prediction_array = np.asarray(raw_prediction)

        if prediction_array.size == 0:
            raise ValueError("MODEL_RETURNED_EMPTY_PREDICTION")

        signal = int(prediction_array.reshape(-1)[0])
        probability, confidence = self._probabilities(
            model=model,
            features=validated,
            signal=signal,
        )

        latency_ms = (perf_counter() - started_at) * 1000.0

        return PredictionResult(
            signal=signal,
            probability=probability,
            confidence=confidence,
            model_id=record.model_id,
            model_name=record.model_name,
            status=record.status,
            quality_score=record.quality_score,
            metrics=dict(record.metrics),
            metadata={
                "experiment_id": record.experiment_id,
                "dataset": record.dataset,
                "strategy": record.strategy,
                "symbol": record.symbol,
                "timeframe": record.timeframe,
                "git_commit": record.git_commit,
                "artifact_path": record.artifact_path,
                "latency_ms": round(latency_ms, 6),
                "feature_rows": int(validated.shape[0]),
                "feature_count": int(validated.shape[1]),
                "cache_hit": cache_hit,
            },
        )

    def clear_cache(self) -> None:
        self._cached_model = None
        self._cached_model_id = None

    def cached_model_id(self) -> str | None:
        return self._cached_model_id

    def _get_production_model(
        self,
        record: ModelRecord,
        *,
        verify_artifact: bool,
    ) -> tuple[Any, bool]:
        if self._cached_model is not None and self._cached_model_id == record.model_id:
            return self._cached_model, True

        model = self.model_loader.load_by_id(
            record.model_id,
            verify=verify_artifact,
        )

        self._cached_model = model
        self._cached_model_id = record.model_id

        return model, False

    @staticmethod
    def _probabilities(
        *,
        model: Any,
        features: np.ndarray,
        signal: int,
    ) -> tuple[float | None, float | None]:
        if not hasattr(model, "predict_proba"):
            return None, None

        raw_probabilities = model.predict_proba(features)
        probabilities = np.asarray(
            raw_probabilities,
            dtype=float,
        )

        if probabilities.ndim != 2:
            raise ValueError("INVALID_PROBABILITY_SHAPE")

        if probabilities.shape[0] == 0:
            raise ValueError("MODEL_RETURNED_EMPTY_PROBABILITIES")

        first_row = probabilities[0]

        if first_row.size == 0:
            raise ValueError("MODEL_RETURNED_EMPTY_PROBABILITIES")

        confidence = float(np.max(first_row))

        if first_row.size == 2:
            probability = float(first_row[1])
        elif 0 <= signal < first_row.size:
            probability = float(first_row[signal])
        else:
            probability = confidence

        return probability, confidence

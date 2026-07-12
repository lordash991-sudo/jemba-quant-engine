from __future__ import annotations

from typing import Any

from jemba_core.ai.inference.feature_validator import FeatureValidator
from jemba_core.ai.inference.inference_service import InferenceService
from jemba_core.ai.inference.prediction_result import PredictionResult


class PredictorEngine:
    """
    High level prediction engine.

    Responsibilities:

    - Validate incoming features.
    - Execute inference.
    - Return PredictionResult.
    """

    def __init__(
        self,
        inference_service: InferenceService,
        validator: FeatureValidator,
    ) -> None:

        self._service = inference_service
        self._validator = validator

    def predict(
        self,
        features: Any,
    ) -> PredictionResult:

        validated = self._validator.validate(features)

        return self._service.predict(validated)

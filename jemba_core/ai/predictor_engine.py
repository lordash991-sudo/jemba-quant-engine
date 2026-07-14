from __future__ import annotations

from typing import Any

from jemba_core.ai.inference.feature_validator import FeatureValidator
from jemba_core.ai.inference.inference_service import InferenceService
from jemba_core.ai.inference.prediction_result import PredictionResult


class PredictorEngine:
    """
    High-level prediction engine.

    Puede crearse vacío para conservar compatibilidad con PipelineEngine:

        PredictorEngine()

    O con sus dependencias completas:

        PredictorEngine(
            inference_service=service,
            validator=validator,
        )
    """

    def __init__(
        self,
        inference_service: InferenceService | None = None,
        validator: FeatureValidator | None = None,
    ) -> None:
        self._service = inference_service
        self._validator = validator or FeatureValidator()

    @property
    def is_configured(self) -> bool:
        """Indica si existe un servicio de inferencia disponible."""
        return self._service is not None

    def configure(
        self,
        inference_service: InferenceService,
        validator: FeatureValidator | None = None,
    ) -> None:
        """
        Configura o reemplaza las dependencias después de crear el motor.
        """
        self._service = inference_service

        if validator is not None:
            self._validator = validator

    def predict(
        self,
        features: Any,
    ) -> PredictionResult:
        """
        Valida las features y ejecuta la inferencia.

        Raises:
            RuntimeError: si no se configuró InferenceService.
            ValueError/TypeError: si las features son inválidas.
        """
        if self._service is None:
            raise RuntimeError("PREDICTOR_ENGINE_NOT_CONFIGURED")

        validated = self._validator.validate(features)

        return self._service.predict(validated)

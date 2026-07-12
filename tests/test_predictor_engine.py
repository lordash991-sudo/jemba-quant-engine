from __future__ import annotations

from unittest.mock import Mock

import numpy as np
import pytest

from jemba_core.ai.inference.prediction_result import PredictionResult
from jemba_core.ai.predictor_engine import PredictorEngine


def make_result() -> PredictionResult:
    return PredictionResult(
        signal=1,
        probability=0.91,
        confidence=0.91,
        model_id="MODEL-001",
        model_name="RandomForest",
        status="production",
        quality_score=88.5,
        metrics={"profit_factor": 2.4},
        metadata={"symbol": "BTCUSDT"},
    )


def test_predict_validates_features_and_calls_service():
    validator = Mock()
    service = Mock()

    validated = np.array([[1.0, 2.0]])
    expected = make_result()

    validator.validate.return_value = validated
    service.predict.return_value = expected

    engine = PredictorEngine(
        inference_service=service,
        validator=validator,
    )

    raw_features = [[1.0, 2.0]]
    result = engine.predict(raw_features)

    validator.validate.assert_called_once_with(raw_features)
    service.predict.assert_called_once_with(validated)

    assert result is expected


def test_returns_prediction_result():
    validator = Mock()
    service = Mock()

    validator.validate.return_value = np.array([[1.0, 2.0]])
    service.predict.return_value = make_result()

    engine = PredictorEngine(
        inference_service=service,
        validator=validator,
    )

    result = engine.predict([[1.0, 2.0]])

    assert isinstance(result, PredictionResult)
    assert result.signal == 1
    assert result.probability == 0.91
    assert result.model_name == "RandomForest"


def test_propagates_validator_error():
    validator = Mock()
    service = Mock()

    validator.validate.side_effect = ValueError("FEATURES_CONTAIN_NAN")

    engine = PredictorEngine(
        inference_service=service,
        validator=validator,
    )

    with pytest.raises(
        ValueError,
        match="FEATURES_CONTAIN_NAN",
    ):
        engine.predict([[1.0, np.nan]])

    service.predict.assert_not_called()


def test_propagates_inference_error():
    validator = Mock()
    service = Mock()

    validator.validate.return_value = np.array([[1.0, 2.0]])
    service.predict.side_effect = LookupError("NO_PRODUCTION_MODEL")

    engine = PredictorEngine(
        inference_service=service,
        validator=validator,
    )

    with pytest.raises(
        LookupError,
        match="NO_PRODUCTION_MODEL",
    ):
        engine.predict([[1.0, 2.0]])


def test_accepts_numpy_array():
    validator = Mock()
    service = Mock()

    features = np.array([[1.0, 2.0]])
    validator.validate.return_value = features
    service.predict.return_value = make_result()

    engine = PredictorEngine(
        inference_service=service,
        validator=validator,
    )

    result = engine.predict(features)

    assert result.signal == 1
    validator.validate.assert_called_once_with(features)

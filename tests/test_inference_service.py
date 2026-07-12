from __future__ import annotations

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

from jemba_core.ai.inference import (
    FeatureValidator,
    InferenceService,
)
from jemba_core.ai.registry_core import (
    ArtifactStore,
    JsonRegistryStorage,
    ModelLoader,
    ModelRegistry,
)


def build_system(tmp_path):
    registry = ModelRegistry(JsonRegistryStorage(tmp_path / "registry.json"))
    artifact_store = ArtifactStore(tmp_path / "artifacts")
    loader = ModelLoader(
        registry,
        artifact_store,
    )
    validator = FeatureValidator(expected_features=2)
    service = InferenceService(
        loader,
        validator,
    )

    return registry, artifact_store, service


def train_model() -> RandomForestClassifier:
    features = np.array(
        [
            [0.0, 0.0],
            [0.5, 0.4],
            [1.0, 1.1],
            [2.0, 2.1],
            [3.0, 3.0],
            [4.0, 4.2],
        ]
    )
    target = np.array([0, 0, 0, 1, 1, 1])

    model = RandomForestClassifier(
        n_estimators=25,
        random_state=42,
    )
    model.fit(features, target)

    return model


def register_production_model(
    registry,
    artifact_store,
):
    model = train_model()

    record = registry.register(
        experiment_id="EXP-INFERENCE-001",
        model_name="RandomForest",
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
        symbol="BTCUSDT",
        timeframe="1h",
        status="production",
        metrics={
            "profit_factor": 2.4,
            "sharpe": 1.9,
            "max_drawdown": 6.0,
            "win_rate": 62.0,
            "expectancy": 0.4,
        },
        parameters={
            "n_estimators": 25,
            "random_state": 42,
        },
    )

    artifact_store.save(
        model,
        model_id=record.model_id,
        model_name=record.model_name,
        metadata={
            "experiment_id": record.experiment_id,
            "status": record.status,
        },
    )

    return record


def test_predicts_with_production_model(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    record = register_production_model(
        registry,
        artifact_store,
    )

    result = service.predict([[3.5, 3.7]])

    assert result.signal in {0, 1}
    assert result.model_id == record.model_id
    assert result.model_name == "RandomForest"
    assert result.status == "production"
    assert result.quality_score > 0


def test_returns_probability_and_confidence(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    register_production_model(
        registry,
        artifact_store,
    )

    result = service.predict([[3.5, 3.7]])

    assert result.probability is not None
    assert result.confidence is not None
    assert 0.0 <= result.probability <= 1.0
    assert 0.0 <= result.confidence <= 1.0


def test_returns_model_metrics_and_metadata(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    register_production_model(
        registry,
        artifact_store,
    )

    result = service.predict([[3.5, 3.7]])

    assert result.metrics["profit_factor"] == 2.4
    assert result.metrics["sharpe"] == 1.9
    assert result.metadata["dataset"] == "BTCUSDT_1H"
    assert result.metadata["symbol"] == "BTCUSDT"
    assert result.metadata["feature_count"] == 2
    assert result.metadata["latency_ms"] >= 0.0


def test_uses_model_cache_after_first_prediction(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    record = register_production_model(
        registry,
        artifact_store,
    )

    first = service.predict([[0.2, 0.1]])
    second = service.predict([[3.5, 3.7]])

    assert first.metadata["cache_hit"] is False
    assert second.metadata["cache_hit"] is True
    assert service.cached_model_id() == record.model_id


def test_clear_cache_forces_model_reload(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    register_production_model(
        registry,
        artifact_store,
    )

    service.predict([[0.2, 0.1]])
    service.clear_cache()

    result = service.predict([[3.5, 3.7]])

    assert result.metadata["cache_hit"] is False
    assert service.cached_model_id() is not None


def test_rejects_invalid_features(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    register_production_model(
        registry,
        artifact_store,
    )

    with pytest.raises(
        ValueError,
        match="FEATURES_CONTAIN_NAN",
    ):
        service.predict([[1.0, np.nan]])


def test_rejects_wrong_feature_count(tmp_path):
    registry, artifact_store, service = build_system(tmp_path)
    register_production_model(
        registry,
        artifact_store,
    )

    with pytest.raises(
        ValueError,
        match="FEATURE_COUNT_MISMATCH",
    ):
        service.predict([[1.0]])


def test_requires_production_model(tmp_path):
    _, _, service = build_system(tmp_path)

    with pytest.raises(
        LookupError,
        match="NO_PRODUCTION_MODEL",
    ):
        service.predict([[1.0, 2.0]])

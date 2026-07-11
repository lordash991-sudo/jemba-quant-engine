from __future__ import annotations

import pytest
from sklearn.ensemble import RandomForestClassifier

from jemba_core.ai.registry_core import (
    ArtifactStore,
    JsonRegistryStorage,
    ModelLoader,
    ModelRegistry,
)


def make_model(
    random_state: int,
) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=5,
        random_state=random_state,
    )

    model.fit(
        [[0.0], [1.0], [2.0], [3.0]],
        [0, 0, 1, 1],
    )

    return model


def make_system(tmp_path):
    registry = ModelRegistry(JsonRegistryStorage(tmp_path / "registry.json"))
    artifact_store = ArtifactStore(tmp_path / "artifacts")
    loader = ModelLoader(
        registry,
        artifact_store,
    )

    return registry, artifact_store, loader


def register_and_save(
    registry,
    artifact_store,
    *,
    experiment_id,
    model_name,
    status,
    random_state,
    metrics=None,
):
    record = registry.register(
        experiment_id=experiment_id,
        model_name=model_name,
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
        status=status,
        metrics=metrics or {},
    )

    model = make_model(random_state)

    artifact_store.save(
        model,
        model_id=record.model_id,
        model_name=record.model_name,
        metadata={
            "experiment_id": record.experiment_id,
            "status": record.status,
        },
    )

    return record, model


def test_loads_model_by_id(tmp_path):
    registry, artifact_store, loader = make_system(tmp_path)

    record, original = register_and_save(
        registry,
        artifact_store,
        experiment_id="EXP-001",
        model_name="RandomForest",
        status="research",
        random_state=42,
    )

    loaded = loader.load_by_id(record.model_id)

    expected = original.predict([[0.0], [3.0]]).tolist()
    actual = loaded.predict([[0.0], [3.0]]).tolist()

    assert actual == expected


def test_loads_production_model(tmp_path):
    registry, artifact_store, loader = make_system(tmp_path)

    record, _ = register_and_save(
        registry,
        artifact_store,
        experiment_id="EXP-002",
        model_name="RandomForest",
        status="production",
        random_state=43,
    )

    loaded = loader.load_production()

    assert loaded is not None
    assert loader.production_record().model_id == (record.model_id)


def test_loads_champion_model(tmp_path):
    registry, artifact_store, loader = make_system(tmp_path)

    record, _ = register_and_save(
        registry,
        artifact_store,
        experiment_id="EXP-003",
        model_name="RandomForest",
        status="champion",
        random_state=44,
    )

    loaded = loader.load_champion()

    assert loaded is not None
    assert loader.champion_record().model_id == (record.model_id)


def test_loads_best_model_by_quality_score(tmp_path):
    registry, artifact_store, loader = make_system(tmp_path)

    register_and_save(
        registry,
        artifact_store,
        experiment_id="EXP-004",
        model_name="RandomForest",
        status="candidate",
        random_state=45,
        metrics={
            "profit_factor": 1.2,
            "sharpe": 0.5,
            "max_drawdown": 20.0,
        },
    )

    best_record, _ = register_and_save(
        registry,
        artifact_store,
        experiment_id="EXP-005",
        model_name="RandomForest",
        status="candidate",
        random_state=46,
        metrics={
            "profit_factor": 2.5,
            "sharpe": 2.0,
            "max_drawdown": 5.0,
            "win_rate": 62.0,
            "expectancy": 0.5,
        },
    )

    loaded = loader.load_best(status="candidate")

    assert loaded is not None
    assert registry.best(status="candidate").model_id == best_record.model_id


def test_raises_when_production_is_missing(tmp_path):
    _, _, loader = make_system(tmp_path)

    with pytest.raises(
        LookupError,
        match="NO_PRODUCTION_MODEL",
    ):
        loader.load_production()


def test_raises_when_champion_is_missing(tmp_path):
    _, _, loader = make_system(tmp_path)

    with pytest.raises(
        LookupError,
        match="NO_CHAMPION_MODEL",
    ):
        loader.load_champion()


def test_raises_when_no_models_exist(tmp_path):
    _, _, loader = make_system(tmp_path)

    with pytest.raises(
        LookupError,
        match="NO_MODEL_AVAILABLE",
    ):
        loader.load_best()


def test_detects_corrupted_production_artifact(
    tmp_path,
):
    registry, artifact_store, loader = make_system(tmp_path)

    record, _ = register_and_save(
        registry,
        artifact_store,
        experiment_id="EXP-006",
        model_name="RandomForest",
        status="production",
        random_state=47,
    )

    paths = artifact_store._paths(
        model_id=record.model_id,
        model_name=record.model_name,
    )

    with paths["artifact"].open("ab") as file:
        file.write(b"corruption")

    with pytest.raises(
        ValueError,
        match="ARTIFACT_CHECKSUM_MISMATCH",
    ):
        loader.load_production()

from __future__ import annotations

import json

import pytest
from sklearn.ensemble import RandomForestClassifier

from jemba_core.ai.registry_core import ArtifactStore


def make_model() -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=5,
        random_state=42,
    )
    model.fit(
        [[0.0], [1.0], [2.0], [3.0]],
        [0, 0, 1, 1],
    )
    return model


def test_saves_artifact_metadata_and_checksum(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    record = store.save(
        make_model(),
        model_id="MODEL-001",
        model_name="RandomForest",
        metadata={
            "dataset": "BTCUSDT_1H",
            "profit_factor": 2.4,
        },
    )

    assert record.model_id == "MODEL-001"
    assert record.sha256
    assert record.metadata["dataset"] == "BTCUSDT_1H"
    assert record.metadata["profit_factor"] == 2.4

    assert (tmp_path / "artifacts" / "randomforest" / ("MODEL-001.joblib")).exists()
    assert (tmp_path / "artifacts" / "randomforest" / ("MODEL-001.json")).exists()
    assert (tmp_path / "artifacts" / "randomforest" / ("MODEL-001.sha256")).exists()


def test_loads_saved_model(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    original = make_model()

    store.save(
        original,
        model_id="MODEL-002",
        model_name="RandomForest",
    )

    loaded = store.load(
        model_id="MODEL-002",
        model_name="RandomForest",
    )

    assert loaded.predict([[0.0], [3.0]]).tolist() == (
        original.predict([[0.0], [3.0]]).tolist()
    )


def test_verifies_valid_checksum(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    store.save(
        make_model(),
        model_id="MODEL-003",
        model_name="RandomForest",
    )

    assert store.verify(
        model_id="MODEL-003",
        model_name="RandomForest",
    )


def test_detects_modified_artifact(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    record = store.save(
        make_model(),
        model_id="MODEL-004",
        model_name="RandomForest",
    )

    with open(record.artifact_path, "ab") as file:
        file.write(b"corruption")

    assert not store.verify(
        model_id="MODEL-004",
        model_name="RandomForest",
    )

    with pytest.raises(
        ValueError,
        match="ARTIFACT_CHECKSUM_MISMATCH",
    ):
        store.load(
            model_id="MODEL-004",
            model_name="RandomForest",
        )


def test_reads_metadata(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    store.save(
        make_model(),
        model_id="MODEL-005",
        model_name="CatBoost",
        metadata={
            "symbol": "BTCUSDT",
            "timeframe": "1h",
        },
    )

    metadata = store.read_metadata(
        model_id="MODEL-005",
        model_name="CatBoost",
    )

    assert metadata["symbol"] == "BTCUSDT"
    assert metadata["timeframe"] == "1h"
    assert len(metadata["sha256"]) == 64


def test_lists_artifacts(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    store.save(
        make_model(),
        model_id="MODEL-006",
        model_name="RandomForest",
    )
    store.save(
        make_model(),
        model_id="MODEL-007",
        model_name="XGBoost",
    )

    assert len(store.list_artifacts()) == 2
    assert len(store.list_artifacts("RandomForest")) == 1


def test_deletes_artifact_files(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    record = store.save(
        make_model(),
        model_id="MODEL-008",
        model_name="RandomForest",
    )

    store.delete(
        model_id="MODEL-008",
        model_name="RandomForest",
    )

    assert not store.verify(
        model_id="MODEL-008",
        model_name="RandomForest",
    )
    assert not (tmp_path / "artifacts" / "randomforest" / "MODEL-008.json").exists()
    assert not (tmp_path / "artifacts" / "randomforest" / "MODEL-008.sha256").exists()
    assert not (tmp_path / "artifacts" / "randomforest" / "MODEL-008.joblib").exists()
    assert record.model_id == "MODEL-008"


def test_rejects_unsafe_identifier(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    with pytest.raises(
        ValueError,
        match="INVALID_ARTIFACT_IDENTIFIER",
    ):
        store.save(
            make_model(),
            model_id="../MODEL-009",
            model_name="RandomForest",
        )


def test_metadata_is_valid_json(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")

    record = store.save(
        make_model(),
        model_id="MODEL-010",
        model_name="RandomForest",
    )

    with open(
        record.metadata_path,
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data["model_id"] == "MODEL-010"
    assert data["model_name"] == "RandomForest"

from __future__ import annotations

import json

import pytest

from jemba_core.ai.registry_core import (
    JsonRegistryStorage,
    ModelRegistry,
)


def make_registry(tmp_path):
    storage = JsonRegistryStorage(tmp_path / "registry.json")
    return ModelRegistry(storage)


def test_registers_and_persists_model(tmp_path):
    registry = make_registry(tmp_path)

    record = registry.register(
        experiment_id="EXP-001",
        model_name="CatBoost",
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
        symbol="BTCUSDT",
        timeframe="1h",
        git_commit="abc1234",
        artifact_path="models/catboost.pkl",
        metrics={
            "profit_factor": 2.4,
            "sharpe": 1.9,
            "max_drawdown": 6.0,
            "win_rate": 62.0,
            "expectancy": 0.4,
        },
        parameters={"depth": 6},
    )

    assert record.model_id.startswith("MODEL-")
    assert record.status == "research"
    assert record.quality_score > 0

    loaded = registry.get(record.model_id)

    assert loaded.model_name == "CatBoost"
    assert loaded.experiment_id == "EXP-001"
    assert loaded.parameters["depth"] == 6


def test_lists_models_by_status(tmp_path):
    registry = make_registry(tmp_path)

    registry.register(
        experiment_id="EXP-001",
        model_name="RandomForest",
        dataset="BTCUSDT_1H",
        strategy="baseline",
        status="research",
    )

    registry.register(
        experiment_id="EXP-002",
        model_name="XGBoost",
        dataset="BTCUSDT_1H",
        strategy="candidate",
        status="candidate",
    )

    assert len(registry.list_models()) == 2
    assert len(registry.list_models(status="candidate")) == 1


def test_best_returns_highest_quality_model(tmp_path):
    registry = make_registry(tmp_path)

    registry.register(
        experiment_id="EXP-001",
        model_name="RandomForest",
        dataset="BTCUSDT_1H",
        strategy="baseline",
        metrics={
            "profit_factor": 1.3,
            "sharpe": 0.8,
            "max_drawdown": 15.0,
        },
    )

    best_record = registry.register(
        experiment_id="EXP-002",
        model_name="CatBoost",
        dataset="BTCUSDT_1H",
        strategy="improved",
        metrics={
            "profit_factor": 2.5,
            "sharpe": 2.0,
            "max_drawdown": 5.0,
            "win_rate": 60.0,
            "expectancy": 0.5,
        },
    )

    result = registry.best()

    assert result is not None
    assert result.model_id == best_record.model_id


def test_updates_model_status(tmp_path):
    registry = make_registry(tmp_path)

    record = registry.register(
        experiment_id="EXP-001",
        model_name="XGBoost",
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
    )

    updated = registry.update_status(
        record.model_id,
        "candidate",
    )

    assert updated.status == "candidate"
    assert registry.get(record.model_id).status == ("candidate")


def test_rejects_invalid_status(tmp_path):
    registry = make_registry(tmp_path)

    with pytest.raises(
        ValueError,
        match="INVALID_MODEL_STATUS",
    ):
        registry.register(
            experiment_id="EXP-001",
            model_name="CatBoost",
            dataset="BTCUSDT_1H",
            strategy="btc_1h_v1",
            status="inventado",
        )


def test_registry_file_contains_valid_json(tmp_path):
    storage_path = tmp_path / "registry.json"
    registry = ModelRegistry(JsonRegistryStorage(storage_path))

    registry.register(
        experiment_id="EXP-001",
        model_name="CatBoost",
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
    )

    data = json.loads(storage_path.read_text(encoding="utf-8"))

    assert len(data) == 1
    assert data[0]["model_name"] == "CatBoost"

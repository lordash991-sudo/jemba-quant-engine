from __future__ import annotations

import json

import pytest

from jemba_core.ai.experiment import (
    ExperimentTracker,
    JsonExperimentStorage,
)


def test_tracker_creates_and_saves_experiment(tmp_path):
    storage_path = tmp_path / "experiments.jsonl"
    tracker = ExperimentTracker(JsonExperimentStorage(storage_path))

    tracker.start(
        model_name="CatBoost",
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
        symbol="BTCUSDT",
        timeframe="1h",
        parameters={"depth": 6},
    )

    tracker.log_metrics(
        {
            "profit_factor": 2.31,
            "max_drawdown": 7.4,
            "sharpe": 1.91,
        }
    )
    tracker.log_artifact("model", "models/experiments/model.pkl")

    finished = tracker.finish()

    assert finished.experiment_id.startswith("EXP-")
    assert finished.run_id.startswith("RUN-")
    assert finished.status == "completed"
    assert finished.metrics["profit_factor"] == pytest.approx(2.31)
    assert storage_path.exists()

    records = tracker.list_experiments()

    assert len(records) == 1
    assert records[0]["model_name"] == "CatBoost"
    assert records[0]["dataset"] == "BTCUSDT_1H"
    assert records[0]["parameters"]["depth"] == 6


def test_tracker_requires_started_experiment(tmp_path):
    tracker = ExperimentTracker(JsonExperimentStorage(tmp_path / "experiments.jsonl"))

    with pytest.raises(RuntimeError, match="EXPERIMENT_NOT_STARTED"):
        tracker.log_metrics({"profit_factor": 1.5})


def test_storage_writes_valid_json(tmp_path):
    storage_path = tmp_path / "experiments.jsonl"
    tracker = ExperimentTracker(JsonExperimentStorage(storage_path))

    tracker.start(
        model_name="RandomForest",
        dataset="BTCUSDT_1H",
        strategy="baseline",
    )
    tracker.finish()

    line = storage_path.read_text(encoding="utf-8").strip()
    data = json.loads(line)

    assert data["model_name"] == "RandomForest"
    assert data["status"] == "completed"

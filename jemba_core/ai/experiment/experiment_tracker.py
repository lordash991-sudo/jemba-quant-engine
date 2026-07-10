from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jemba_core.ai.experiment.experiment import Experiment
from jemba_core.ai.experiment.storage import JsonExperimentStorage


class ExperimentTracker:
    def __init__(
        self,
        storage: JsonExperimentStorage | None = None,
    ) -> None:
        self.storage = storage or JsonExperimentStorage()
        self.current: Experiment | None = None

    def start(
        self,
        *,
        model_name: str,
        dataset: str,
        strategy: str,
        symbol: str = "",
        timeframe: str = "",
        parameters: dict[str, Any] | None = None,
    ) -> Experiment:
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid4().hex[:8].upper()

        self.current = Experiment(
            experiment_id=f"EXP-{timestamp}-{suffix}",
            run_id=f"RUN-{timestamp}-{suffix}",
            model_name=model_name,
            dataset=dataset,
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            git_commit=self._git_commit(),
            parameters=parameters or {},
        )

        return self.current

    def log_metrics(self, metrics: dict[str, float]) -> None:
        experiment = self._require_current()
        experiment.metrics.update(
            {name: float(value) for name, value in metrics.items()}
        )

    def log_artifact(self, name: str, path: str) -> None:
        experiment = self._require_current()
        experiment.artifacts[name] = path

    def finish(self, status: str = "completed") -> Experiment:
        experiment = self._require_current()
        experiment.finish(status)
        self.storage.save(experiment)
        self.current = None
        return experiment

    def list_experiments(self) -> list[dict[str, Any]]:
        return self.storage.load_all()

    def _require_current(self) -> Experiment:
        if self.current is None:
            raise RuntimeError("EXPERIMENT_NOT_STARTED")

        return self.current

    @staticmethod
    def _git_commit() -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            return "unknown"

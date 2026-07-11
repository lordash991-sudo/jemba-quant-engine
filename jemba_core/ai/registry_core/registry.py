from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jemba_core.ai.registry_core.metadata import ModelRecord
from jemba_core.ai.registry_core.storage import JsonRegistryStorage


class ModelRegistry:
    VALID_STATUSES = {
        "research",
        "candidate",
        "champion",
        "production",
        "archived",
    }

    def __init__(
        self,
        storage: JsonRegistryStorage | None = None,
    ) -> None:
        self.storage = storage or JsonRegistryStorage()

    def register(
        self,
        *,
        experiment_id: str,
        model_name: str,
        dataset: str,
        strategy: str,
        symbol: str = "",
        timeframe: str = "",
        git_commit: str = "",
        artifact_path: str = "",
        metrics: dict[str, float] | None = None,
        parameters: dict[str, Any] | None = None,
        status: str = "research",
    ) -> ModelRecord:
        self._validate_status(status)

        model_metrics = metrics or {}

        record = ModelRecord(
            model_id=self._generate_model_id(),
            experiment_id=experiment_id,
            model_name=model_name,
            dataset=dataset,
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            git_commit=git_commit,
            artifact_path=artifact_path,
            metrics={name: float(value) for name, value in model_metrics.items()},
            parameters=parameters or {},
            status=status,
            quality_score=self.calculate_quality_score(model_metrics),
        )

        records = self.storage.load_all()
        records.append(record)
        self.storage.save_all(records)

        return record

    def list_models(
        self,
        status: str | None = None,
    ) -> list[ModelRecord]:
        records = self.storage.load_all()

        if status is None:
            return records

        self._validate_status(status)

        return [record for record in records if record.status == status]

    def get(self, model_id: str) -> ModelRecord:
        for record in self.storage.load_all():
            if record.model_id == model_id:
                return record

        raise KeyError(f"MODEL_NOT_FOUND: {model_id}")

    def get_unique_by_status(
        self,
        status: str,
    ) -> ModelRecord | None:
        records = self.list_models(status=status)

        if len(records) > 1:
            raise RuntimeError(f"MULTIPLE_MODELS_WITH_STATUS: {status}")

        return records[0] if records else None

    def best(
        self,
        status: str | None = None,
    ) -> ModelRecord | None:
        records = self.list_models(status=status)

        if not records:
            return None

        return max(
            records,
            key=lambda record: record.quality_score,
        )

    def update_status(
        self,
        model_id: str,
        status: str,
    ) -> ModelRecord:
        self._validate_status(status)

        records = self.storage.load_all()
        updated: ModelRecord | None = None

        for record in records:
            if record.model_id == model_id:
                record.status = status
                updated = record
                break

        if updated is None:
            raise KeyError(f"MODEL_NOT_FOUND: {model_id}")

        self.storage.save_all(records)

        return updated

    @staticmethod
    def calculate_quality_score(
        metrics: dict[str, float],
    ) -> float:
        profit_factor = max(
            float(metrics.get("profit_factor", 0.0)),
            0.0,
        )
        sharpe = max(
            float(metrics.get("sharpe", 0.0)),
            0.0,
        )
        max_drawdown = max(
            float(metrics.get("max_drawdown", 100.0)),
            0.0,
        )
        win_rate = max(
            float(metrics.get("win_rate", 0.0)),
            0.0,
        )
        expectancy = max(
            float(metrics.get("expectancy", 0.0)),
            0.0,
        )

        profit_factor_score = min(profit_factor / 3.0, 1.0)
        sharpe_score = min(sharpe / 3.0, 1.0)
        drawdown_score = max(
            1.0 - (max_drawdown / 30.0),
            0.0,
        )
        win_rate_score = min(win_rate / 100.0, 1.0)
        expectancy_score = min(expectancy, 1.0)

        score = (
            profit_factor_score * 40.0
            + drawdown_score * 25.0
            + sharpe_score * 20.0
            + expectancy_score * 10.0
            + win_rate_score * 5.0
        )

        return round(score, 4)

    @classmethod
    def _validate_status(cls, status: str) -> None:
        if status not in cls.VALID_STATUSES:
            raise ValueError(f"INVALID_MODEL_STATUS: {status}")

    @staticmethod
    def _generate_model_id() -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        suffix = uuid4().hex[:8].upper()

        return f"MODEL-{timestamp}-{suffix}"

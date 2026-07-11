from __future__ import annotations

from typing import Any

from jemba_core.ai.registry_core.artifact_store import ArtifactStore
from jemba_core.ai.registry_core.metadata import ModelRecord
from jemba_core.ai.registry_core.registry import ModelRegistry


class ModelLoader:
    def __init__(
        self,
        registry: ModelRegistry,
        artifact_store: ArtifactStore,
    ) -> None:
        self.registry = registry
        self.artifact_store = artifact_store

    def load_by_id(
        self,
        model_id: str,
        *,
        verify: bool = True,
    ) -> Any:
        record = self.registry.get(model_id)

        return self._load_record(
            record,
            verify=verify,
        )

    def load_production(
        self,
        *,
        verify: bool = True,
    ) -> Any:
        record = self.registry.get_unique_by_status("production")

        if record is None:
            raise LookupError("NO_PRODUCTION_MODEL")

        return self._load_record(
            record,
            verify=verify,
        )

    def load_champion(
        self,
        *,
        verify: bool = True,
    ) -> Any:
        record = self.registry.get_unique_by_status("champion")

        if record is None:
            raise LookupError("NO_CHAMPION_MODEL")

        return self._load_record(
            record,
            verify=verify,
        )

    def load_best(
        self,
        *,
        status: str | None = None,
        verify: bool = True,
    ) -> Any:
        record = self.registry.best(status=status)

        if record is None:
            raise LookupError("NO_MODEL_AVAILABLE")

        return self._load_record(
            record,
            verify=verify,
        )

    def production_record(self) -> ModelRecord:
        record = self.registry.get_unique_by_status("production")

        if record is None:
            raise LookupError("NO_PRODUCTION_MODEL")

        return record

    def champion_record(self) -> ModelRecord:
        record = self.registry.get_unique_by_status("champion")

        if record is None:
            raise LookupError("NO_CHAMPION_MODEL")

        return record

    def _load_record(
        self,
        record: ModelRecord,
        *,
        verify: bool,
    ) -> Any:
        return self.artifact_store.load(
            model_id=record.model_id,
            model_name=record.model_name,
            verify=verify,
        )

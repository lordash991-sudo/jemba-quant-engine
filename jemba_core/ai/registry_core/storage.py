from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jemba_core.ai.registry_core.metadata import ModelRecord


class JsonRegistryStorage:
    def __init__(
        self,
        path: str | Path = "models/registry/registry.json",
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[ModelRecord]:
        if not self.path.exists():
            return []

        content = self.path.read_text(encoding="utf-8").strip()

        if not content:
            return []

        data: list[dict[str, Any]] = json.loads(content)

        return [ModelRecord.from_dict(record) for record in data]

    def save_all(self, records: list[ModelRecord]) -> None:
        payload = [record.to_dict() for record in records]
        temporary_path = self.path.with_suffix(".tmp")

        temporary_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(self.path)

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jemba_core.ai.experiment.experiment import Experiment


class JsonExperimentStorage:
    def __init__(
        self,
        path: str | Path = "experiments/records/experiments.jsonl",
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, experiment: Experiment) -> None:
        with self.path.open("a", encoding="utf-8") as file:
            json.dump(experiment.to_dict(), file, ensure_ascii=False)
            file.write("\n")

    def load_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        records: list[dict[str, Any]] = []

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                clean_line = line.strip()

                if clean_line:
                    records.append(json.loads(clean_line))

        return records

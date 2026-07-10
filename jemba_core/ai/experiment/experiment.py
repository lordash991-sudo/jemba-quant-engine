from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Experiment:
    experiment_id: str
    run_id: str
    model_name: str
    dataset: str
    strategy: str
    symbol: str = ""
    timeframe: str = ""
    git_commit: str = ""
    status: str = "research"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)

    def finish(self, status: str = "completed") -> None:
        self.status = status
        self.finished_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

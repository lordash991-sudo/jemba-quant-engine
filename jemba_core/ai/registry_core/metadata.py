from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class ModelRecord:
    model_id: str
    experiment_id: str
    model_name: str
    dataset: str
    strategy: str
    symbol: str = ""
    timeframe: str = ""
    git_commit: str = ""
    status: str = "research"
    artifact_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metrics: dict[str, float] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelRecord:
        return cls(**data)

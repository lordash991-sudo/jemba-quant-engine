from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    model_id: str
    model_name: str
    artifact_path: str
    metadata_path: str
    checksum_path: str
    sha256: str
    created_at: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

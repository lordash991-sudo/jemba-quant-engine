from __future__ import annotations

from dataclasses import dataclass

from jemba_core.ai.registry_core.metadata import ModelRecord


@dataclass(frozen=True, slots=True)
class PromotionResult:
    promoted_model: ModelRecord
    previous_champion: ModelRecord | None
    previous_production: ModelRecord | None

from __future__ import annotations

from jemba_core.ai.registry_core.metadata import ModelRecord
from jemba_core.ai.registry_core.promotion import PromotionResult
from jemba_core.ai.registry_core.registry import ModelRegistry


class PromotionEngine:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def promote_to_champion(
        self,
        model_id: str,
        *,
        force: bool = False,
    ) -> PromotionResult:
        candidate = self.registry.get(model_id)

        if candidate.status not in {"candidate", "research"}:
            raise ValueError(f"MODEL_NOT_PROMOTABLE: {candidate.status}")

        current_champion = self.registry.get_unique_by_status("champion")
        current_production = self.registry.get_unique_by_status("production")

        if (
            current_champion is not None
            and not force
            and candidate.quality_score <= current_champion.quality_score
        ):
            raise ValueError("CANDIDATE_NOT_BETTER_THAN_CHAMPION")

        if current_champion is not None:
            self.registry.update_status(
                current_champion.model_id,
                "archived",
            )

        promoted = self.registry.update_status(
            candidate.model_id,
            "champion",
        )

        return PromotionResult(
            promoted_model=promoted,
            previous_champion=current_champion,
            previous_production=current_production,
        )

    def promote_to_production(
        self,
        model_id: str,
    ) -> PromotionResult:
        model = self.registry.get(model_id)

        if model.status != "champion":
            raise ValueError("ONLY_CHAMPION_CAN_GO_TO_PRODUCTION")

        current_production = self.registry.get_unique_by_status("production")
        current_champion = self.registry.get_unique_by_status("champion")

        if current_production is not None:
            self.registry.update_status(
                current_production.model_id,
                "archived",
            )

        promoted = self.registry.update_status(
            model.model_id,
            "production",
        )

        return PromotionResult(
            promoted_model=promoted,
            previous_champion=current_champion,
            previous_production=current_production,
        )

    def rollback_production(self) -> ModelRecord:
        production = self.registry.get_unique_by_status("production")
        archived = self.registry.list_models(status="archived")

        if production is None:
            raise ValueError("NO_PRODUCTION_MODEL")

        if not archived:
            raise ValueError("NO_ARCHIVED_MODEL_FOR_ROLLBACK")

        previous = max(
            archived,
            key=lambda record: record.created_at,
        )

        self.registry.update_status(
            production.model_id,
            "archived",
        )

        return self.registry.update_status(
            previous.model_id,
            "production",
        )

    def archive(self, model_id: str) -> ModelRecord:
        return self.registry.update_status(
            model_id,
            "archived",
        )

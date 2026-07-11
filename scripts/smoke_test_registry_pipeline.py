from __future__ import annotations

import shutil
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier

from jemba_core.ai.registry_core import (
    ArtifactStore,
    JsonRegistryStorage,
    ModelLoader,
    ModelRegistry,
    PromotionEngine,
)


def main() -> None:
    root = Path("tmp_smoke_registry")

    if root.exists():
        shutil.rmtree(root)

    registry_path = root / "registry.json"
    artifact_root = root / "artifacts"

    registry = ModelRegistry(JsonRegistryStorage(registry_path))
    artifact_store = ArtifactStore(artifact_root)
    promotion = PromotionEngine(registry)
    loader = ModelLoader(registry, artifact_store)

    x_train = [
        [0.0],
        [1.0],
        [2.0],
        [3.0],
        [4.0],
        [5.0],
    ]
    y_train = [0, 0, 0, 1, 1, 1]

    model = RandomForestClassifier(
        n_estimators=25,
        random_state=42,
    )
    model.fit(x_train, y_train)

    record = registry.register(
        experiment_id="EXP-SMOKE-001",
        model_name="RandomForest",
        dataset="SMOKE_DATASET",
        strategy="smoke_strategy",
        symbol="BTCUSDT",
        timeframe="1h",
        status="candidate",
        metrics={
            "profit_factor": 2.2,
            "sharpe": 1.7,
            "max_drawdown": 6.0,
            "win_rate": 60.0,
            "expectancy": 0.4,
        },
        parameters={
            "n_estimators": 25,
            "random_state": 42,
        },
    )

    artifact = artifact_store.save(
        model,
        model_id=record.model_id,
        model_name=record.model_name,
        metadata={
            "experiment_id": record.experiment_id,
            "dataset": record.dataset,
            "strategy": record.strategy,
        },
    )

    promotion.promote_to_champion(record.model_id)
    promotion.promote_to_production(record.model_id)

    loaded_model = loader.load_production()

    sample = [[0.5], [4.5]]

    original_prediction = model.predict(sample).tolist()
    loaded_prediction = loaded_model.predict(sample).tolist()

    if original_prediction != loaded_prediction:
        raise RuntimeError("PREDICTION_MISMATCH_BETWEEN_ORIGINAL_AND_LOADED_MODEL")

    production_record = loader.production_record()

    if production_record.model_id != record.model_id:
        raise RuntimeError("WRONG_PRODUCTION_MODEL")

    if not artifact_store.verify(
        model_id=record.model_id,
        model_name=record.model_name,
    ):
        raise RuntimeError("ARTIFACT_CHECKSUM_INVALID")

    print("")
    print("SMOKE TEST COMPLETADO")
    print(f"model_id: {record.model_id}")
    print(f"status: {production_record.status}")
    print(f"quality_score: {record.quality_score}")
    print(f"sha256: {artifact.sha256}")
    print(f"prediction_original: {original_prediction}")
    print(f"prediction_loaded:   {loaded_prediction}")
    print(f"registry_path: {registry_path}")
    print(f"artifact_path: {artifact.artifact_path}")
    print("RESULTADO: PASS")


if __name__ == "__main__":
    main()

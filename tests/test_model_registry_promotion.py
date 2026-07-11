from __future__ import annotations

import pytest

from jemba_core.ai.registry_core import (
    JsonRegistryStorage,
    ModelRegistry,
    PromotionEngine,
)


def make_registry(tmp_path):
    storage = JsonRegistryStorage(tmp_path / "registry.json")
    return ModelRegistry(storage)


def register_model(
    registry,
    *,
    experiment_id,
    model_name,
    quality_metrics,
    status="candidate",
):
    return registry.register(
        experiment_id=experiment_id,
        model_name=model_name,
        dataset="BTCUSDT_1H",
        strategy="btc_1h_v1",
        metrics=quality_metrics,
        status=status,
    )


def strong_metrics():
    return {
        "profit_factor": 2.5,
        "sharpe": 2.0,
        "max_drawdown": 5.0,
        "win_rate": 62.0,
        "expectancy": 0.5,
    }


def weak_metrics():
    return {
        "profit_factor": 1.4,
        "sharpe": 0.8,
        "max_drawdown": 18.0,
        "win_rate": 48.0,
        "expectancy": 0.1,
    }


def test_promotes_candidate_to_champion(tmp_path):
    registry = make_registry(tmp_path)
    engine = PromotionEngine(registry)

    candidate = register_model(
        registry,
        experiment_id="EXP-001",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
    )

    result = engine.promote_to_champion(candidate.model_id)

    assert result.promoted_model.status == "champion"
    assert registry.get_unique_by_status("champion").model_id == (candidate.model_id)


def test_archives_previous_champion(tmp_path):
    registry = make_registry(tmp_path)
    engine = PromotionEngine(registry)

    old = register_model(
        registry,
        experiment_id="EXP-001",
        model_name="RandomForest",
        quality_metrics=weak_metrics(),
        status="champion",
    )

    new = register_model(
        registry,
        experiment_id="EXP-002",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
    )

    engine.promote_to_champion(new.model_id)

    assert registry.get(old.model_id).status == "archived"
    assert registry.get(new.model_id).status == "champion"


def test_rejects_weaker_candidate(tmp_path):
    registry = make_registry(tmp_path)
    engine = PromotionEngine(registry)

    register_model(
        registry,
        experiment_id="EXP-001",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
        status="champion",
    )

    weak = register_model(
        registry,
        experiment_id="EXP-002",
        model_name="RandomForest",
        quality_metrics=weak_metrics(),
    )

    with pytest.raises(
        ValueError,
        match="CANDIDATE_NOT_BETTER_THAN_CHAMPION",
    ):
        engine.promote_to_champion(weak.model_id)


def test_promotes_champion_to_production(tmp_path):
    registry = make_registry(tmp_path)
    engine = PromotionEngine(registry)

    champion = register_model(
        registry,
        experiment_id="EXP-001",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
        status="champion",
    )

    result = engine.promote_to_production(champion.model_id)

    assert result.promoted_model.status == "production"
    assert registry.get_unique_by_status("production").model_id == (champion.model_id)


def test_rejects_non_champion_for_production(tmp_path):
    registry = make_registry(tmp_path)
    engine = PromotionEngine(registry)

    candidate = register_model(
        registry,
        experiment_id="EXP-001",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
    )

    with pytest.raises(
        ValueError,
        match="ONLY_CHAMPION_CAN_GO_TO_PRODUCTION",
    ):
        engine.promote_to_production(candidate.model_id)


def test_rollback_restores_latest_archived_model(tmp_path):
    registry = make_registry(tmp_path)
    engine = PromotionEngine(registry)

    archived = register_model(
        registry,
        experiment_id="EXP-001",
        model_name="RandomForest",
        quality_metrics=weak_metrics(),
        status="archived",
    )

    production = register_model(
        registry,
        experiment_id="EXP-002",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
        status="production",
    )

    restored = engine.rollback_production()

    assert restored.model_id == archived.model_id
    assert restored.status == "production"
    assert registry.get(production.model_id).status == "archived"


def test_unique_status_guard(tmp_path):
    registry = make_registry(tmp_path)

    register_model(
        registry,
        experiment_id="EXP-001",
        model_name="CatBoost",
        quality_metrics=strong_metrics(),
        status="champion",
    )

    register_model(
        registry,
        experiment_id="EXP-002",
        model_name="XGBoost",
        quality_metrics=strong_metrics(),
        status="champion",
    )

    with pytest.raises(
        RuntimeError,
        match="MULTIPLE_MODELS_WITH_STATUS",
    ):
        registry.get_unique_by_status("champion")

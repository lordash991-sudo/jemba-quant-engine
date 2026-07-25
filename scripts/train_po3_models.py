from __future__ import annotations

import json
from pathlib import Path

from jemba_core.training.po3_model_competition import (
    CompetitionConfig,
    PO3ModelCompetition,
)


ROOT = Path(".").resolve()

DATASET_DIRECTORY = (
    ROOT
    / "data"
    / "processed"
    / "po3"
)

ARTIFACT_DIRECTORY = (
    ROOT
    / "models"
    / "experiments"
    / "po3_v2"
)

REPORT_DIRECTORY = (
    ROOT
    / "reports"
    / "training"
    / "po3_v2"
)


def find_latest_dataset() -> Path:
    candidates = sorted(
        DATASET_DIRECTORY.glob(
            "BTCUSDT_1h_PO3_V2_*.csv"
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError(
            "NO_PO3_TRAINING_DATASET_FOUND"
        )

    return candidates[0]


def main() -> int:
    dataset_path = find_latest_dataset()

    print("")
    print("=" * 90)
    print("JEMBA - COMPETICION TEMPORAL DE MODELOS PO3")
    print("=" * 90)

    print("DATASET:", dataset_path)
    print("MODO: ENTRENAMIENTO HISTORICO")
    print("ORDENES REALES: DESACTIVADAS")
    print("")

    competition = PO3ModelCompetition(
        CompetitionConfig(
            train_fraction=0.60,
            validation_fraction=0.20,
            test_fraction=0.20,
            random_state=42,
            minimum_total_rows=60,
            minimum_train_rows=30,
            minimum_validation_rows=10,
            minimum_test_rows=10,
            minimum_class_rows=3,
            primary_metric="macro_f1",
        )
    )

    result = competition.run(
        dataset_path=dataset_path,
        artifact_directory=ARTIFACT_DIRECTORY,
        report_directory=REPORT_DIRECTORY,
    )

    print("")
    print("=" * 90)
    print("RESULTADO DE LA COMPETICION")
    print("=" * 90)

    print("FILAS:", result.dataset_rows)
    print("FEATURES:", len(result.feature_columns))
    print("DISTRIBUCION:", result.class_distribution)
    print("SPLITS:", result.split_sizes)

    print("")
    print("MODELOS:")

    for evaluation in result.evaluations:
        validation = evaluation.get(
            "validation_metrics",
            {},
        )

        print(
            f"- {evaluation['model_name']}: "
            f"{evaluation['status']} | "
            f"macro_f1="
            f"{validation.get('macro_f1', 'N/A')} | "
            f"balanced_accuracy="
            f"{validation.get('balanced_accuracy', 'N/A')} | "
            f"duration="
            f"{evaluation['duration_seconds']}s"
        )

        if evaluation.get("error"):
            print(
                "  ERROR:",
                evaluation["error"],
            )

    print("")
    print("CHAMPION:", result.champion_name)
    print(
        "VALIDATION SCORE:",
        round(
            result.champion_validation_score,
            6,
        ),
    )

    print("")
    print("TEST METRICS:")
    print(
        json.dumps(
            result.champion_test_metrics,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("")
    print("ARTIFACT:", result.artifact_path)
    print("METADATA:", result.metadata_path)
    print("REPORT:", result.report_path)

    print("")
    print("PO3 MODEL COMPETITION: PASS")
    print("MODELO GUARDADO COMO EXPERIMENTO")
    print("NO SE REGISTRO COMO PRODUCTION")
    print("NO SE EJECUTARON PREDICCIONES LIVE")
    print("NO SE ABRIERON POSICIONES")
    print("NO SE ENVIARON ORDENES")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
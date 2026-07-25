from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from jemba_core.training.po3_model_competition import (
    CompetitionConfig,
    LEAKAGE_COLUMNS,
    PO3ModelCompetition,
)


def make_dataset(
    rows: int = 150,
) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    timestamp = pd.date_range(
        "2025-01-01",
        periods=rows,
        freq="h",
        tz="UTC",
    )

    feature_1 = rng.normal(
        0.0,
        1.0,
        rows,
    )

    feature_2 = rng.normal(
        0.0,
        1.0,
        rows,
    )

    labels = np.resize(
        np.array([-1, 0, 1]),
        rows,
    )

    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "FEATURE_1": feature_1,
            "FEATURE_2": feature_2,
            "LABEL": labels,
            "LABEL_NAME": [
                "STOP_LOSS"
                if label == -1
                else "EXPIRED"
                if label == 0
                else "TAKE_PROFIT"
                for label in labels
            ],
            "EXIT_PRICE": 100.0,
            "R_MULTIPLE": labels.astype(float),
        }
    )


def test_split_fractions_must_sum_to_one() -> None:
    with pytest.raises(
        ValueError,
        match="SPLIT_FRACTIONS_MUST_SUM_TO_1",
    ):
        CompetitionConfig(
            train_fraction=0.50,
            validation_fraction=0.30,
            test_fraction=0.30,
        )


def test_feature_selection_excludes_leakage() -> None:
    competition = PO3ModelCompetition(
        CompetitionConfig(
            minimum_total_rows=30,
            minimum_train_rows=10,
            minimum_validation_rows=5,
            minimum_test_rows=5,
        )
    )

    frame = make_dataset()

    features = competition.select_feature_columns(
        frame
    )

    assert "FEATURE_1" in features
    assert "FEATURE_2" in features

    assert not (
        set(features)
        & LEAKAGE_COLUMNS
    )


def test_temporal_split_preserves_order() -> None:
    competition = PO3ModelCompetition(
        CompetitionConfig(
            minimum_total_rows=30,
            minimum_train_rows=10,
            minimum_validation_rows=5,
            minimum_test_rows=5,
        )
    )

    frame = make_dataset(150)

    features = competition.select_feature_columns(
        frame
    )

    split = competition.temporal_split(
        frame=frame,
        feature_columns=features,
    )

    assert len(split.X_train) == 90
    assert len(split.X_validation) == 30
    assert len(split.X_test) == 30

    assert (
        split.X_train.index.max()
        < split.X_validation.index.min()
    )

    assert (
        split.X_validation.index.max()
        < split.X_test.index.min()
    )


def test_class_distribution_contains_names() -> None:
    competition = PO3ModelCompetition()

    distribution = competition.class_distribution(
        pd.Series([-1, -1, 0, 1])
    )

    assert distribution[
        "-1_STOP_LOSS"
    ] == 2

    assert distribution[
        "0_EXPIRED"
    ] == 1

    assert distribution[
        "1_TAKE_PROFIT"
    ] == 1


def test_random_forest_can_train_and_evaluate() -> None:
    competition = PO3ModelCompetition(
        CompetitionConfig(
            minimum_total_rows=30,
            minimum_train_rows=10,
            minimum_validation_rows=5,
            minimum_test_rows=5,
        )
    )

    frame = make_dataset(180)

    features = competition.select_feature_columns(
        frame
    )

    split = competition.temporal_split(
        frame=frame,
        feature_columns=features,
    )

    factory = competition.build_candidates()[
        "RandomForest"
    ]

    evaluation, model = (
        competition._train_candidate(
            model_name="RandomForest",
            factory=factory,
            split=split,
        )
    )

    assert evaluation.status == "PASS"
    assert model is not None

    assert (
        0.0
        <= evaluation.validation_metrics[
            "macro_f1"
        ]
        <= 1.0
    )


def test_insufficient_rows_are_rejected() -> None:
    competition = PO3ModelCompetition()

    with pytest.raises(
        ValueError,
        match="INSUFFICIENT_DATASET_ROWS",
    ):
        competition.validate_dataset(
            make_dataset(20)
        )
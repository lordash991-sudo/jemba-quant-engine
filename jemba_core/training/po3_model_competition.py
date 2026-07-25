from __future__ import annotations

import json
import math
import time
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from sklearn.base import ClassifierMixin
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
)
from sklearn.utils.class_weight import compute_sample_weight


TARGET_COLUMN = "LABEL"

LABEL_ORDER = (-1, 0, 1)

LABEL_NAMES = {
    -1: "STOP_LOSS",
    0: "EXPIRED",
    1: "TAKE_PROFIT",
}

LEAKAGE_COLUMNS = {
    "LABEL",
    "LABEL_NAME",
    "ENTRY_PRICE",
    "STOP_LOSS",
    "TAKE_PROFIT",
    "EXIT_PRICE",
    "EXIT_BAR_INDEX",
    "BARS_TO_EXIT",
    "RETURN_PCT",
    "R_MULTIPLE",
    "MFE_PCT",
    "MAE_PCT",
    "HIT_TP",
    "HIT_SL",
    "EXPIRED",
    "AMBIGUOUS_HIT",
}

NON_FEATURE_COLUMNS = {
    "date",
    "timestamp",
    "close_time",
    "open_time",
    "datetime",
}


@dataclass(frozen=True)
class CompetitionConfig:
    train_fraction: float = 0.60
    validation_fraction: float = 0.20
    test_fraction: float = 0.20

    random_state: int = 42

    minimum_total_rows: int = 60
    minimum_train_rows: int = 30
    minimum_validation_rows: int = 10
    minimum_test_rows: int = 10
    minimum_class_rows: int = 3

    primary_metric: str = "macro_f1"

    def __post_init__(self) -> None:
        total = (
            self.train_fraction
            + self.validation_fraction
            + self.test_fraction
        )

        if not math.isclose(total, 1.0, abs_tol=1e-9):
            raise ValueError(
                "SPLIT_FRACTIONS_MUST_SUM_TO_1"
            )

        if min(
            self.train_fraction,
            self.validation_fraction,
            self.test_fraction,
        ) <= 0:
            raise ValueError(
                "SPLIT_FRACTIONS_MUST_BE_POSITIVE"
            )

        if self.primary_metric not in {
            "macro_f1",
            "balanced_accuracy",
            "weighted_f1",
        }:
            raise ValueError(
                "PRIMARY_METRIC_NOT_SUPPORTED"
            )


@dataclass
class DatasetSplit:
    X_train: pd.DataFrame
    y_train: pd.Series

    X_validation: pd.DataFrame
    y_validation: pd.Series

    X_test: pd.DataFrame
    y_test: pd.Series


@dataclass
class ModelEvaluation:
    model_name: str
    available: bool
    status: str
    duration_seconds: float
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any] | None
    error: str | None = None


@dataclass
class CompetitionResult:
    created_at: str
    dataset_path: str
    feature_columns: list[str]
    dataset_rows: int
    class_distribution: dict[str, int]
    split_sizes: dict[str, int]
    champion_name: str
    primary_metric: str
    champion_validation_score: float
    champion_test_metrics: dict[str, Any]
    evaluations: list[dict[str, Any]]
    artifact_path: str
    metadata_path: str
    report_path: str


class PO3ModelCompetition:
    """
    Competición temporal de modelos supervisados PO3.

    El test permanece aislado hasta seleccionar al ganador
    usando únicamente el conjunto de validación.
    """

    def __init__(
        self,
        config: CompetitionConfig | None = None,
    ) -> None:
        self.config = config or CompetitionConfig()

    def run(
        self,
        *,
        dataset_path: str | Path,
        artifact_directory: str | Path,
        report_directory: str | Path,
    ) -> CompetitionResult:
        dataset_path = Path(dataset_path).resolve()
        artifact_directory = Path(artifact_directory).resolve()
        report_directory = Path(report_directory).resolve()

        frame = self.load_dataset(dataset_path)

        feature_columns = self.select_feature_columns(frame)

        split = self.temporal_split(
            frame=frame,
            feature_columns=feature_columns,
        )

        candidates = self.build_candidates()

        evaluations: list[ModelEvaluation] = []
        trained_models: dict[str, ClassifierMixin] = {}

        for model_name, factory in candidates.items():
            evaluation, model = self._train_candidate(
                model_name=model_name,
                factory=factory,
                split=split,
            )

            evaluations.append(evaluation)

            if model is not None:
                trained_models[model_name] = model

        valid_evaluations = [
            evaluation
            for evaluation in evaluations
            if evaluation.status == "PASS"
            and evaluation.model_name in trained_models
        ]

        if not valid_evaluations:
            errors = {
                evaluation.model_name: evaluation.error
                for evaluation in evaluations
            }

            raise RuntimeError(
                f"NO_MODEL_COMPLETED_TRAINING: {errors}"
            )

        champion_evaluation = max(
            valid_evaluations,
            key=self._validation_score,
        )

        champion_name = champion_evaluation.model_name
        champion_model = trained_models[champion_name]

        champion_test_metrics = self.evaluate(
            model=champion_model,
            X=split.X_test,
            y=split.y_test,
        )

        for evaluation in evaluations:
            if evaluation.model_name == champion_name:
                evaluation.test_metrics = champion_test_metrics
                break

        artifact_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        safe_name = (
            champion_name
            .strip()
            .lower()
            .replace(" ", "_")
        )

        artifact_path = (
            artifact_directory
            / f"PO3_{safe_name}_{timestamp}.joblib"
        )

        metadata_path = (
            artifact_directory
            / f"PO3_{safe_name}_{timestamp}.json"
        )

        report_path = (
            report_directory
            / f"po3_model_competition_{timestamp}.json"
        )

        artifact_payload = {
            "model": champion_model,
            "feature_columns": feature_columns,
            "label_order": list(LABEL_ORDER),
            "label_names": LABEL_NAMES,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "dataset_path": str(dataset_path),
            "competition_config": asdict(self.config),
        }

        joblib.dump(
            artifact_payload,
            artifact_path,
        )

        metadata = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "model_name": champion_name,
            "feature_columns": feature_columns,
            "feature_count": len(feature_columns),
            "label_order": list(LABEL_ORDER),
            "label_names": LABEL_NAMES,
            "dataset_path": str(dataset_path),
            "dataset_rows": len(frame),
            "class_distribution": self.class_distribution(
                frame[TARGET_COLUMN]
            ),
            "split_sizes": {
                "train": len(split.X_train),
                "validation": len(split.X_validation),
                "test": len(split.X_test),
            },
            "primary_metric": self.config.primary_metric,
            "validation_metrics": (
                champion_evaluation.validation_metrics
            ),
            "test_metrics": champion_test_metrics,
            "competition_config": asdict(self.config),
        }

        metadata_path.write_text(
            json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False,
                default=self._json_default,
            ),
            encoding="utf-8",
        )

        report = {
            **metadata,
            "evaluations": [
                asdict(evaluation)
                for evaluation in evaluations
            ],
            "artifact_path": str(artifact_path),
            "metadata_path": str(metadata_path),
        }

        report_path.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
                default=self._json_default,
            ),
            encoding="utf-8",
        )

        return CompetitionResult(
            created_at=metadata["created_at"],
            dataset_path=str(dataset_path),
            feature_columns=feature_columns,
            dataset_rows=len(frame),
            class_distribution=metadata[
                "class_distribution"
            ],
            split_sizes=metadata["split_sizes"],
            champion_name=champion_name,
            primary_metric=self.config.primary_metric,
            champion_validation_score=float(
                self._validation_score(
                    champion_evaluation
                )
            ),
            champion_test_metrics=champion_test_metrics,
            evaluations=[
                asdict(evaluation)
                for evaluation in evaluations
            ],
            artifact_path=str(artifact_path),
            metadata_path=str(metadata_path),
            report_path=str(report_path),
        )

    def load_dataset(
        self,
        dataset_path: str | Path,
    ) -> pd.DataFrame:
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(
                f"DATASET_NOT_FOUND: {path}"
            )

        frame = pd.read_csv(
            path,
            low_memory=False,
        )

        if frame.empty:
            raise ValueError(
                "TRAINING_DATASET_IS_EMPTY"
            )

        if TARGET_COLUMN not in frame.columns:
            raise ValueError(
                "TARGET_COLUMN_LABEL_NOT_FOUND"
            )

        frame[TARGET_COLUMN] = pd.to_numeric(
            frame[TARGET_COLUMN],
            errors="coerce",
        )

        frame = frame[
            frame[TARGET_COLUMN].isin(
                LABEL_ORDER
            )
        ].copy()

        frame[TARGET_COLUMN] = (
            frame[TARGET_COLUMN]
            .astype(int)
        )

        frame = self._sort_temporally(frame)

        frame.reset_index(
            drop=True,
            inplace=True,
        )

        self.validate_dataset(frame)

        return frame

    def validate_dataset(
        self,
        frame: pd.DataFrame,
    ) -> None:
        if len(frame) < self.config.minimum_total_rows:
            raise ValueError(
                "INSUFFICIENT_DATASET_ROWS: "
                f"{len(frame)} < "
                f"{self.config.minimum_total_rows}"
            )

        distribution = frame[
            TARGET_COLUMN
        ].value_counts()

        if len(distribution) < 2:
            raise ValueError(
                "TARGET_REQUIRES_AT_LEAST_TWO_CLASSES"
            )

        rare_classes = {
            int(label): int(count)
            for label, count in distribution.items()
            if count < self.config.minimum_class_rows
        }

        if rare_classes:
            raise ValueError(
                f"INSUFFICIENT_CLASS_ROWS: {rare_classes}"
            )

    def select_feature_columns(
        self,
        frame: pd.DataFrame,
    ) -> list[str]:
        excluded = (
            LEAKAGE_COLUMNS
            | NON_FEATURE_COLUMNS
        )

        candidates = [
            column
            for column in frame.columns
            if column not in excluded
        ]

        numeric_features: list[str] = []

        for column in candidates:
            converted = pd.to_numeric(
                frame[column],
                errors="coerce",
            )

            if converted.notna().any():
                frame[column] = converted
                numeric_features.append(column)

        if not numeric_features:
            raise ValueError(
                "NO_NUMERIC_FEATURE_COLUMNS_AVAILABLE"
            )

        forbidden_found = sorted(
            set(numeric_features)
            & LEAKAGE_COLUMNS
        )

        if forbidden_found:
            raise RuntimeError(
                f"DATA_LEAKAGE_COLUMNS_FOUND: "
                f"{forbidden_found}"
            )

        return numeric_features

    def temporal_split(
        self,
        *,
        frame: pd.DataFrame,
        feature_columns: list[str],
    ) -> DatasetSplit:
        usable = frame[
            feature_columns
            + [TARGET_COLUMN]
        ].copy()

        usable.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True,
        )

        usable.dropna(
            subset=feature_columns
            + [TARGET_COLUMN],
            inplace=True,
        )

        usable.reset_index(
            drop=True,
            inplace=True,
        )

        total_rows = len(usable)

        train_end = int(
            total_rows
            * self.config.train_fraction
        )

        validation_end = int(
            total_rows
            * (
                self.config.train_fraction
                + self.config.validation_fraction
            )
        )

        train = usable.iloc[
            :train_end
        ].copy()

        validation = usable.iloc[
            train_end:validation_end
        ].copy()

        test = usable.iloc[
            validation_end:
        ].copy()

        if len(train) < self.config.minimum_train_rows:
            raise ValueError(
                f"INSUFFICIENT_TRAIN_ROWS: {len(train)}"
            )

        if (
            len(validation)
            < self.config.minimum_validation_rows
        ):
            raise ValueError(
                "INSUFFICIENT_VALIDATION_ROWS: "
                f"{len(validation)}"
            )

        if len(test) < self.config.minimum_test_rows:
            raise ValueError(
                f"INSUFFICIENT_TEST_ROWS: {len(test)}"
            )

        return DatasetSplit(
            X_train=train[feature_columns],
            y_train=train[TARGET_COLUMN],
            X_validation=validation[
                feature_columns
            ],
            y_validation=validation[
                TARGET_COLUMN
            ],
            X_test=test[feature_columns],
            y_test=test[TARGET_COLUMN],
        )

    def build_candidates(
        self,
    ) -> dict[str, Any]:
        candidates: dict[str, Any] = {
            "RandomForest": lambda: RandomForestClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=2,
                max_features="sqrt",
                class_weight="balanced_subsample",
                random_state=self.config.random_state,
                n_jobs=-1,
            ),
            "ExtraTrees": lambda: ExtraTreesClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=2,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.config.random_state,
                n_jobs=-1,
            ),
            "HistGradientBoosting": (
                lambda: HistGradientBoostingClassifier(
                    learning_rate=0.05,
                    max_iter=300,
                    max_leaf_nodes=31,
                    l2_regularization=1.0,
                    random_state=self.config.random_state,
                )
            ),
        }

        try:
            from xgboost import XGBClassifier

            candidates["XGBoost"] = (
                lambda: XGBClassifier(
                    n_estimators=400,
                    max_depth=5,
                    learning_rate=0.04,
                    subsample=0.80,
                    colsample_bytree=0.80,
                    objective="multi:softprob",
                    eval_metric="mlogloss",
                    random_state=self.config.random_state,
                    n_jobs=-1,
                )
            )
        except ImportError:
            pass

        try:
            from lightgbm import LGBMClassifier

            candidates["LightGBM"] = (
                lambda: LGBMClassifier(
                    n_estimators=400,
                    learning_rate=0.04,
                    num_leaves=31,
                    subsample=0.80,
                    colsample_bytree=0.80,
                    class_weight="balanced",
                    random_state=self.config.random_state,
                    n_jobs=-1,
                    verbosity=-1,
                )
            )
        except ImportError:
            pass

        try:
            from catboost import CatBoostClassifier

            candidates["CatBoost"] = (
                lambda: CatBoostClassifier(
                    iterations=400,
                    depth=6,
                    learning_rate=0.04,
                    loss_function="MultiClass",
                    auto_class_weights="Balanced",
                    random_seed=self.config.random_state,
                    verbose=False,
                )
            )
        except ImportError:
            pass

        return candidates

    def evaluate(
        self,
        *,
        model: ClassifierMixin,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> dict[str, Any]:
        prediction = model.predict(X)

        metrics: dict[str, Any] = {
            "rows": len(X),
            "accuracy": float(
                accuracy_score(y, prediction)
            ),
            "balanced_accuracy": float(
                balanced_accuracy_score(
                    y,
                    prediction,
                )
            ),
            "macro_f1": float(
                f1_score(
                    y,
                    prediction,
                    labels=list(LABEL_ORDER),
                    average="macro",
                    zero_division=0,
                )
            ),
            "weighted_f1": float(
                f1_score(
                    y,
                    prediction,
                    labels=list(LABEL_ORDER),
                    average="weighted",
                    zero_division=0,
                )
            ),
            "macro_precision": float(
                precision_score(
                    y,
                    prediction,
                    labels=list(LABEL_ORDER),
                    average="macro",
                    zero_division=0,
                )
            ),
            "macro_recall": float(
                recall_score(
                    y,
                    prediction,
                    labels=list(LABEL_ORDER),
                    average="macro",
                    zero_division=0,
                )
            ),
            "confusion_matrix": (
                confusion_matrix(
                    y,
                    prediction,
                    labels=list(LABEL_ORDER),
                )
                .tolist()
            ),
            "classification_report": (
                classification_report(
                    y,
                    prediction,
                    labels=list(LABEL_ORDER),
                    target_names=[
                        LABEL_NAMES[label]
                        for label in LABEL_ORDER
                    ],
                    output_dict=True,
                    zero_division=0,
                )
            ),
            "prediction_distribution": {
                str(int(label)): int(count)
                for label, count in pd.Series(
                    prediction
                ).value_counts().items()
            },
            "actual_distribution": (
                self.class_distribution(y)
            ),
        }

        if hasattr(model, "predict_proba"):
            try:
                probabilities = model.predict_proba(X)

                model_classes = [
                    int(value)
                    for value in model.classes_
                ]

                probability_frame = pd.DataFrame(
                    probabilities,
                    columns=model_classes,
                    index=X.index,
                )

                aligned_probabilities = (
                    probability_frame
                    .reindex(
                        columns=list(LABEL_ORDER),
                        fill_value=0.0,
                    )
                    .to_numpy()
                )

                metrics["log_loss"] = float(
                    log_loss(
                        y,
                        aligned_probabilities,
                        labels=list(LABEL_ORDER),
                    )
                )
            except Exception as error:
                metrics["log_loss_error"] = (
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        return metrics

    def _train_candidate(
        self,
        *,
        model_name: str,
        factory: Any,
        split: DatasetSplit,
    ) -> tuple[
        ModelEvaluation,
        ClassifierMixin | None,
    ]:
        started = time.perf_counter()

        try:
            model = factory()

            fit_parameters: dict[str, Any] = {}

            if model_name in {
                "HistGradientBoosting",
            }:
                fit_parameters["sample_weight"] = (
                    compute_sample_weight(
                        class_weight="balanced",
                        y=split.y_train,
                    )
                )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                model.fit(
                    split.X_train,
                    split.y_train,
                    **fit_parameters,
                )

            validation_metrics = self.evaluate(
                model=model,
                X=split.X_validation,
                y=split.y_validation,
            )

            duration = (
                time.perf_counter()
                - started
            )

            return (
                ModelEvaluation(
                    model_name=model_name,
                    available=True,
                    status="PASS",
                    duration_seconds=round(
                        duration,
                        6,
                    ),
                    validation_metrics=(
                        validation_metrics
                    ),
                    test_metrics=None,
                    error=None,
                ),
                model,
            )

        except Exception as error:
            duration = (
                time.perf_counter()
                - started
            )

            return (
                ModelEvaluation(
                    model_name=model_name,
                    available=True,
                    status="FAIL",
                    duration_seconds=round(
                        duration,
                        6,
                    ),
                    validation_metrics={},
                    test_metrics=None,
                    error=(
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                ),
                None,
            )

    def _validation_score(
        self,
        evaluation: ModelEvaluation,
    ) -> float:
        return float(
            evaluation.validation_metrics.get(
                self.config.primary_metric,
                float("-inf"),
            )
        )

    @staticmethod
    def class_distribution(
        values: pd.Series,
    ) -> dict[str, int]:
        distribution = (
            pd.Series(values)
            .value_counts()
            .sort_index()
        )

        return {
            f"{int(label)}_{LABEL_NAMES.get(int(label), 'UNKNOWN')}": int(count)
            for label, count in distribution.items()
        }

    @staticmethod
    def _sort_temporally(
        frame: pd.DataFrame,
    ) -> pd.DataFrame:
        for column in (
            "timestamp",
            "date",
            "datetime",
            "open_time",
        ):
            if column not in frame.columns:
                continue

            parsed = pd.to_datetime(
                frame[column],
                errors="coerce",
                utc=True,
            )

            if parsed.notna().any():
                result = frame.copy()
                result["_temporal_sort"] = parsed

                result.sort_values(
                    "_temporal_sort",
                    inplace=True,
                    kind="stable",
                )

                result.drop(
                    columns=["_temporal_sort"],
                    inplace=True,
                )

                return result

        return frame.copy()

    @staticmethod
    def _json_default(
        value: Any,
    ) -> Any:
        if isinstance(value, np.integer):
            return int(value)

        if isinstance(value, np.floating):
            return float(value)

        if isinstance(value, np.ndarray):
            return value.tolist()

        raise TypeError(
            f"NOT_JSON_SERIALIZABLE: "
            f"{type(value).__name__}"
        )
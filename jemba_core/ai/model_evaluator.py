from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float | None
    confusion_matrix: np.ndarray
    classification_report: dict


class ModelEvaluator:
    def evaluate(
        self,
        *,
        y_true,
        y_pred,
        y_score=None,
    ) -> EvaluationResult:

        accuracy = float(accuracy_score(y_true, y_pred))

        precision = float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        )

        recall = float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        )

        f1 = float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        )

        roc_auc = None

        if y_score is not None:
            roc_auc = float(
                roc_auc_score(
                    y_true,
                    y_score,
                )
            )

        matrix = confusion_matrix(
            y_true,
            y_pred,
        )

        report = classification_report(
            y_true,
            y_pred,
            output_dict=True,
            zero_division=0,
        )

        return EvaluationResult(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            roc_auc=roc_auc,
            confusion_matrix=matrix,
            classification_report=report,
        )

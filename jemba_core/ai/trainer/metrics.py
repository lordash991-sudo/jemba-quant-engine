from __future__ import annotations

from dataclasses import dataclass

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


@dataclass
class MetricsResult:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float


class MetricsEngine:

    def evaluate(
        self,
        y_true,
        y_pred,
        y_prob,
    ) -> MetricsResult:

        return MetricsResult(
            accuracy=accuracy_score(y_true, y_pred),
            precision=precision_score(y_true, y_pred),
            recall=recall_score(y_true, y_pred),
            f1=f1_score(y_true, y_pred),
            roc_auc=roc_auc_score(y_true, y_prob),
        )

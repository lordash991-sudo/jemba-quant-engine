from __future__ import annotations

import numpy as np

from jemba_core.ai.model_evaluator import (
    EvaluationResult,
    ModelEvaluator,
)


def test_metrics_are_calculated():

    evaluator = ModelEvaluator()

    y_true = np.array([0, 1, 1, 0, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 1, 1])
    y_score = np.array([0.1, 0.9, 0.4, 0.2, 0.8, 0.6])

    result = evaluator.evaluate(
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
    )

    assert isinstance(result, EvaluationResult)

    assert 0 <= result.accuracy <= 1
    assert 0 <= result.precision <= 1
    assert 0 <= result.recall <= 1
    assert 0 <= result.f1 <= 1
    assert 0 <= result.roc_auc <= 1


def test_confusion_matrix_shape():

    evaluator = ModelEvaluator()

    result = evaluator.evaluate(
        y_true=[0, 1, 0, 1],
        y_pred=[0, 1, 1, 0],
    )

    assert result.confusion_matrix.shape == (2, 2)


def test_report_contains_precision():

    evaluator = ModelEvaluator()

    result = evaluator.evaluate(
        y_true=[0, 1, 0, 1],
        y_pred=[0, 1, 1, 0],
    )

    assert "accuracy" in result.classification_report

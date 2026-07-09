from __future__ import annotations

import numpy as np

from jemba_core.ai.trainer.metrics import ModelMetrics


def test_accuracy():

    y_true = np.array([1,0,1,1,0,1])

    y_pred = np.array([1,0,1,0,0,1])

    metrics = ModelMetrics().evaluate(y_true,y_pred)

    assert metrics["accuracy"] > 0.7


def test_keys():

    y_true=np.array([1,0])

    y_pred=np.array([1,0])

    metrics=ModelMetrics().evaluate(y_true,y_pred)

    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics

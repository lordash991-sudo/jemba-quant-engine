from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.trainer.metrics import MetricsEngine
from jemba_core.ai.trainer.splitter import DatasetSplitter


def sample():
    np.random.seed(42)

    return pd.DataFrame(
        {
            "ema20": np.random.rand(100),
            "rsi": np.random.rand(100),
            "target": np.random.randint(0, 2, 100),
        }
    )


def test_split():
    split = DatasetSplitter().split(sample())

    assert len(split.X_train) == 70
    assert len(split.X_valid) == 15
    assert len(split.X_test) == 15
    assert "target" not in split.X_train.columns


def test_metrics():
    y_true = np.array([1, 0, 1, 1, 0, 1])
    y_pred = np.array([1, 0, 1, 0, 0, 1])
    y_prob = np.array([0.95, 0.10, 0.80, 0.45, 0.30, 0.99])

    result = MetricsEngine().evaluate(
        y_true,
        y_pred,
        y_prob,
    )

    assert result.accuracy > 0
    assert result.precision > 0
    assert result.recall > 0
    assert result.f1 > 0
    assert result.roc_auc > 0

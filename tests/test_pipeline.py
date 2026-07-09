from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.trainer.pipeline import TrainingPipeline


def sample():
    np.random.seed(42)

    return pd.DataFrame(
        {
            "ema20": np.random.rand(200),
            "rsi": np.random.rand(200),
            "atr": np.random.rand(200),
            "target": np.random.randint(0, 2, 200),
        }
    )


def test_pipeline_fit():

    pipeline = TrainingPipeline()

    result = pipeline.prepare(sample())

    assert result.X_train.shape[0] > 0
    assert result.X_valid.shape[0] > 0
    assert result.X_test.shape[0] > 0


def test_pipeline_columns():

    pipeline = TrainingPipeline()

    result = pipeline.prepare(sample())

    assert "target" not in result.X_train.columns

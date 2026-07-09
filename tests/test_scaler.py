from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.trainer.scaler import FeatureScaler


def sample():
    np.random.seed(42)

    return pd.DataFrame(
        {
            "ema20": np.random.rand(100),
            "rsi": np.random.rand(100),
            "atr": np.random.rand(100),
        }
    )


def test_fit_transform():
    scaler = FeatureScaler()

    scaled = scaler.fit_transform(sample())

    assert scaled.shape == (100, 3)


def test_transform():
    scaler = FeatureScaler()

    scaler.fit(sample())

    scaled = scaler.transform(sample())

    assert scaled.shape == (100, 3)

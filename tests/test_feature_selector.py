from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.feature_selector import FeatureSelector


def sample():

    np.random.seed(1)

    ema20 = np.arange(100)

    ema21 = ema20 + 0.00001

    rsi = np.random.randint(30, 70, 100)

    return pd.DataFrame(
        {
            "ema20": ema20,
            "ema21": ema21,
            "rsi": rsi,
        }
    )


def test_correlation_filter():

    selector = FeatureSelector(0.95)

    result = selector.fit_transform(sample())

    assert len(result.columns) == 2
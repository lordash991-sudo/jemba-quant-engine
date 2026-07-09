from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.feature_selector import FeatureSelector


def sample():
    np.random.seed(1)

    ema20 = np.arange(100)
    ema21 = ema20 + 0.00001
    rsi = np.random.randint(30, 70, 100)
    target = (ema20 > 50).astype(int)

    return pd.DataFrame(
        {
            "ema20": ema20,
            "ema21": ema21,
            "rsi": rsi,
            "constant": 1,
            "target": target,
        }
    )


def test_correlation_filter():
    selector = FeatureSelector(0.95)

    result = selector.fit_transform(sample().drop(columns=["target"]))

    assert len(result.columns) == 2


def test_mutual_information_selector_uses_target():
    selector = FeatureSelector(
        correlation_threshold=0.95,
        max_features=1,
        target_column="target",
    )

    result = selector.fit_transform(sample())

    assert len(result.columns) == 1
    assert result.columns[0] in selector.feature_scores
    assert "target" not in result.columns

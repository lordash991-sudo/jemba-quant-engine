from __future__ import annotations

import pandas as pd

from jemba_core.ai.feature_selector import FeatureSelector


def sample():
    return pd.DataFrame(
        {
            "ema20": [1, 2, 3],
            "ema50": [2, 3, 4],
            "constant": [1, 1, 1],
            "rsi": [40, 50, 60],
        }
    )


def test_constant_columns_removed():
    selector = FeatureSelector()

    result = selector.fit_transform(sample())

    assert "constant" not in result.columns
    assert len(result.columns) == 3
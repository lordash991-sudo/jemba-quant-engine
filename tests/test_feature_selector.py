import numpy as np
import pandas as pd

from jemba_core.ai.feature_selector import FeatureSelector


def test_feature_selector():

    rng = np.random.default_rng(42)

    df = pd.DataFrame(
        {
            "ema": rng.random(300),
            "atr": rng.random(300),
            "volume": rng.random(300),
            "momentum": rng.random(300),
            "volatility": rng.random(300),
            "label": rng.integers(0, 2, 300),
        }
    )

    selector = FeatureSelector()

    importance = selector.fit(df)

    assert len(importance) == 5

    reduced = selector.select(df, top_k=3)

    assert len(reduced.columns) == 4
    assert "label" in reduced.columns

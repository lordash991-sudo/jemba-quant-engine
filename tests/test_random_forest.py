from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.models.random_forest import RandomForestEngine


def sample():

    np.random.seed(42)

    return pd.DataFrame(
        {
            "a": np.random.randn(200),
            "b": np.random.randn(200),
            "target": np.random.randint(0, 2, 200),
        }
    )


def test_fit():

    df = sample()

    model = RandomForestEngine()

    model.fit(df.drop(columns=["target"]), df["target"])

    assert model.model is not None


def test_predict():

    df = sample()

    model = RandomForestEngine()

    model.fit(df.drop(columns=["target"]), df["target"])

    pred = model.predict(df.drop(columns=["target"]))

    assert len(pred) == len(df)

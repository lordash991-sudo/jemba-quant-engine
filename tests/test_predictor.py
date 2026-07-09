from __future__ import annotations

import numpy as np
import pandas as pd

from jemba_core.ai.models.random_forest import RandomForestEngine
from jemba_core.ai.predictor import PredictionEngine


def sample():

    np.random.seed(42)

    return pd.DataFrame(
        {
            "a": np.random.randn(300),
            "b": np.random.randn(300),
            "target": np.random.randint(0, 2, 300),
        }
    )


def test_prediction():

    df = sample()

    model = RandomForestEngine()

    model.fit(df.drop(columns=["target"]), df["target"])

    predictor = PredictionEngine(model)

    probs = predictor.predict_proba(df.drop(columns=["target"]))

    assert len(probs) == len(df)


def test_signal():

    df = sample()

    model = RandomForestEngine()

    model.fit(df.drop(columns=["target"]), df["target"])

    predictor = PredictionEngine(model)

    signal = predictor.predict(df.drop(columns=["target"]))

    assert len(signal) == len(df)

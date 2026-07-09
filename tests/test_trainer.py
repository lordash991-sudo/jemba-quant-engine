from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from jemba_core.ai.trainer.trainer import ModelTrainer


def sample():

    np.random.seed(42)

    return pd.DataFrame(
        {
            "ema20": np.random.rand(300),
            "rsi": np.random.rand(300),
            "atr": np.random.rand(300),
            "target": np.random.randint(0, 2, 300),
        }
    )


def test_train():

    trainer = ModelTrainer(RandomForestClassifier())

    model = trainer.fit(sample())

    assert model is not None


def test_predict():

    trainer = ModelTrainer(RandomForestClassifier())

    trainer.fit(sample())

    predictions = trainer.predict(sample().drop(columns=["target"]))

    assert len(predictions) == 300

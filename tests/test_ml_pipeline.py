import numpy as np
import pandas as pd

from jemba_core.ai.ml_pipeline import MLPipeline


def test_ml_pipeline():

    rng = np.random.default_rng(42)

    df = pd.DataFrame({

        "ema": rng.random(400),

        "atr": rng.random(400),

        "momentum": rng.random(400),

        "volume": rng.random(400),

        "label": rng.integers(0,2,400),

    })

    model,result = MLPipeline().train(df)

    assert result.accuracy >= 0

    assert result.precision >= 0

    assert result.recall >= 0

    assert result.f1 >= 0

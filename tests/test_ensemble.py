import numpy as np
import pandas as pd

from jemba_core.ai.ensemble_inference import EnsembleInference


def test_ensemble():

    rng = np.random.default_rng(42)

    X = pd.DataFrame(
        {
            "ema": rng.random(500),
            "atr": rng.random(500),
            "volume": rng.random(500),
            "momentum": rng.random(500),
        }
    )

    y = rng.integers(0, 2, 500)

    ensemble = EnsembleInference()

    ensemble.fit(X, y)

    prediction = ensemble.predict(X)

    probability = ensemble.predict_proba(X)

    assert len(prediction) == 500

    assert probability.shape[0] == 500

from unittest.mock import MagicMock

import pandas as pd

from jemba_core.ai.predictor_engine import PredictorEngine


def dataframe():

    return pd.DataFrame({
        "ema_20":[1,2,3],
        "ema_50":[2,3,4],
        "atr_14":[1.1,1.2,1.3],
        "rsi_14":[40,55,70],
    })


def test_without_model():

    engine = PredictorEngine()

    result = engine.predict(dataframe())

    assert len(result.columns) == 4


def test_prediction():

    model = MagicMock()

    model.predict.return_value = [1,0,1]

    model.predict_proba.return_value = [
        [0.20,0.80],
        [0.70,0.30],
        [0.10,0.90],
    ]

    engine = PredictorEngine(model)

    result = engine.predict(dataframe())

    assert "prediction" in result.columns
    assert "probability_long" in result.columns
    assert "probability_short" in result.columns

    assert result.iloc[-1]["prediction"] == 1


def test_latest():

    model = MagicMock()

    model.predict.return_value = [1,0,1]

    model.predict_proba.return_value = [
        [0.20,0.80],
        [0.70,0.30],
        [0.10,0.90],
    ]

    engine = PredictorEngine(model)

    latest = engine.latest(dataframe())

    assert latest["prediction"] == 1

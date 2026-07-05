from pathlib import Path

from jemba_core.ai.predictor import Predictor


def test_predictor_load():

    model = Predictor(
        Path("models/trained/SOLUSDT_random_forest.pkl")
    )

    assert model.model is not None

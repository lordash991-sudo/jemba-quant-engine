from jemba_core.ai.predictor_service import PredictorService


def test_predictor_service_model_path():
    service = PredictorService()
    path = service._model_path("SOL-USDT")

    assert str(path).endswith("SOLUSDT_random_forest.pkl")

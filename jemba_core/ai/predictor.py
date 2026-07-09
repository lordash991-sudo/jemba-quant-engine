from __future__ import annotations

import numpy as np


class PredictionEngine:
    def __init__(self, model):
        self.model = model

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        probs = self.model.predict_proba(X)
        return np.asarray(probs)[:, 1]


class Predictor(PredictionEngine):
    pass

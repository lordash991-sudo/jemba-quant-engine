from jemba_core.ai.ensemble import EnsembleFactory


class EnsembleInference:

    def __init__(self):

        self.model = EnsembleFactory.build()

    def fit(self, X, y):

        self.model.fit(X, y)

    def predict(self, X):

        return self.model.predict(X)

    def predict_proba(self, X):

        return self.model.predict_proba(X)

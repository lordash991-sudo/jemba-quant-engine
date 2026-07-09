from __future__ import annotations

import pandas as pd

from jemba_core.ai.trainer.pipeline import TrainingPipeline


class ModelTrainer:

    def __init__(self, model):

        self.model = model
        self.pipeline = TrainingPipeline()

    def fit(self, df: pd.DataFrame):

        split = self.pipeline.prepare(df)

        self.model.fit(split.X_train, split.y_train)

        return self.model

    def predict(self, X: pd.DataFrame):

        X = self.pipeline.scaler.transform(X)

        return self.model.predict(X)

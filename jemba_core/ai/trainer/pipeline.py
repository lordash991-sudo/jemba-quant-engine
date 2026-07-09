from __future__ import annotations

import pandas as pd

from jemba_core.ai.trainer.scaler import FeatureScaler
from jemba_core.ai.trainer.splitter import DatasetSplitter


class TrainingPipeline:
    def __init__(self):
        self.scaler = FeatureScaler()
        self.splitter = DatasetSplitter()

    def prepare(self, df: pd.DataFrame):
        split = self.splitter.split(df)

        split.X_train = self.scaler.fit_transform(split.X_train)
        split.X_valid = self.scaler.transform(split.X_valid)
        split.X_test = self.scaler.transform(split.X_test)

        return split

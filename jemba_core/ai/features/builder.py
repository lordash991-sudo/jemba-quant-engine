from __future__ import annotations

import pandas as pd

from jemba_core.ai.features.trend import TrendFeatures


class FeatureBuilder:
    def __init__(self):
        self.trend = TrendFeatures()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        data = self.trend.transform(data)
        return data

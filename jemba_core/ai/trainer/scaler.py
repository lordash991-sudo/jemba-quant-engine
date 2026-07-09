from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import StandardScaler


class FeatureScaler:
    def __init__(self):
        self.scaler = StandardScaler()
        self.columns: list[str] = []

    def fit(self, df: pd.DataFrame) -> None:
        self.columns = list(df.columns)
        self.scaler.fit(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        scaled = self.scaler.transform(df[self.columns])

        return pd.DataFrame(
            scaled,
            columns=self.columns,
            index=df.index,
        )

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)

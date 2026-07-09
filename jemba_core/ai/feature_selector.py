from __future__ import annotations

import pandas as pd


class FeatureSelector:
    """
    Selecciona las variables útiles para el entrenamiento.
    """

    def __init__(self):
        self.selected_features: list[str] = []

    def fit(self, df: pd.DataFrame) -> None:
        self.selected_features = list(df.columns)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.selected_features].copy()

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)
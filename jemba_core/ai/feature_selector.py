from __future__ import annotations

import pandas as pd


class FeatureSelector:
    """
    Selecciona variables útiles para entrenamiento.
    """

    def __init__(self):
        self.selected_features: list[str] = []

    def remove_constant_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.loc[:, df.nunique(dropna=False) > 1]

    def fit(self, df: pd.DataFrame) -> None:
        data = self.remove_constant_columns(df)
        self.selected_features = list(data.columns)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.selected_features].copy()

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)
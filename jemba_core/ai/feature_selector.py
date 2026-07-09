from __future__ import annotations

import numpy as np
import pandas as pd


class FeatureSelector:
    """
    Intelligent Feature Selection.
    """

    def __init__(self, correlation_threshold: float = 0.95):
        self.selected_features: list[str] = []
        self.correlation_threshold = correlation_threshold

    def remove_constant_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.loc[:, df.nunique(dropna=False) > 1]

    def remove_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.T.drop_duplicates().T

    def remove_correlated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        corr = df.corr(numeric_only=True).abs()

        upper = corr.where(
            np.triu(np.ones(corr.shape), k=1).astype(bool)
        )

        drop = [
            column
            for column in upper.columns
            if any(upper[column] > self.correlation_threshold)
        ]

        return df.drop(columns=drop)

    def fit(self, df: pd.DataFrame) -> None:
        data = self.remove_constant_columns(df)
        data = self.remove_duplicate_columns(data)
        data = self.remove_correlated_columns(data)

        self.selected_features = list(data.columns)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.selected_features].copy()

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)

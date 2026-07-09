from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif


class FeatureSelector:
    """
    Intelligent Feature Selection.
    """

    def __init__(
        self,
        correlation_threshold: float = 0.95,
        max_features: int | None = None,
        target_column: str = "target",
    ):
        self.selected_features: list[str] = []
        self.feature_scores: dict[str, float] = {}
        self.correlation_threshold = correlation_threshold
        self.max_features = max_features
        self.target_column = target_column

    def remove_constant_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.loc[:, df.nunique(dropna=False) > 1]

    def remove_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.T.drop_duplicates().T

    def remove_correlated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        corr = df.corr(numeric_only=True).abs()

        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

        drop = [
            column
            for column in upper.columns
            if any(upper[column] > self.correlation_threshold)
        ]

        return df.drop(columns=drop)

    def rank_by_mutual_information(
        self,
        df: pd.DataFrame,
        target: pd.Series,
    ) -> list[str]:
        numeric = df.select_dtypes(include=["number"]).copy()
        numeric = numeric.replace([np.inf, -np.inf], np.nan).fillna(0)

        scores = mutual_info_classif(
            numeric,
            target,
            discrete_features=False,
            random_state=42,
        )

        self.feature_scores = dict(zip(numeric.columns, scores, strict=True))

        ranked = sorted(
            self.feature_scores,
            key=self.feature_scores.get,
            reverse=True,
        )

        if self.max_features is not None:
            return ranked[: self.max_features]

        return ranked

    def fit(self, df: pd.DataFrame) -> None:
        if self.target_column not in df.columns:
            data = self.remove_constant_columns(df)
            data = self.remove_duplicate_columns(data)
            data = self.remove_correlated_columns(data)
            self.selected_features = list(data.columns)
            return

        target = df[self.target_column]
        features = df.drop(columns=[self.target_column])

        data = self.remove_constant_columns(features)
        data = self.remove_duplicate_columns(data)
        data = self.remove_correlated_columns(data)

        self.selected_features = self.rank_by_mutual_information(
            data,
            target,
        )

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.selected_features].copy()

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)

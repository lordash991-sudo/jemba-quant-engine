from __future__ import annotations

from typing import Sequence

import pandas as pd
from sklearn.ensemble import RandomForestClassifier


class FeatureSelector:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.importances_: pd.Series | None = None

    def fit(
        self,
        df: pd.DataFrame,
        target: str = "label",
    ) -> pd.Series:

        features = df.drop(columns=[target])
        labels = df[target]

        model = RandomForestClassifier(
            n_estimators=200,
            random_state=self.random_state,
            n_jobs=-1,
        )

        model.fit(features, labels)

        self.importances_ = (
            pd.Series(
                model.feature_importances_,
                index=features.columns,
            )
            .sort_values(ascending=False)
        )

        return self.importances_

    def select(
        self,
        df: pd.DataFrame,
        top_k: int = 25,
        target: str = "label",
    ) -> pd.DataFrame:

        if self.importances_ is None:
            self.fit(df, target)

        selected = list(self.importances_.head(top_k).index)

        return df[selected + [target]]

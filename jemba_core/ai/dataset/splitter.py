from __future__ import annotations

import pandas as pd


class DatasetSplitter:
    def split(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        validation_ratio: float = 0.15,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        if not 0 < train_ratio < 1:
            raise ValueError("INVALID_TRAIN_RATIO")

        if not 0 < validation_ratio < 1:
            raise ValueError("INVALID_VALIDATION_RATIO")

        train_end = int(len(df) * train_ratio)
        validation_end = int(len(df) * (train_ratio + validation_ratio))

        train = df.iloc[:train_end].reset_index(drop=True)
        validation = df.iloc[train_end:validation_end].reset_index(drop=True)
        test = df.iloc[validation_end:].reset_index(drop=True)

        return train, validation, test

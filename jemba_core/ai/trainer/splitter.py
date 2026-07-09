from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class DatasetSplit:
    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series
    y_test: pd.Series


class DatasetSplitter:

    def __init__(
        self,
        target_column: str = "target",
        train_size: float = 0.70,
        valid_size: float = 0.15,
    ):
        self.target_column = target_column
        self.train_size = train_size
        self.valid_size = valid_size

    def split(self, df: pd.DataFrame) -> DatasetSplit:

        if self.target_column not in df.columns:
            raise ValueError(
                f"Target column '{self.target_column}' not found."
            )

        n = len(df)

        train_end = int(n * self.train_size)
        valid_end = int(n * (self.train_size + self.valid_size))

        train = df.iloc[:train_end]
        valid = df.iloc[train_end:valid_end]
        test = df.iloc[valid_end:]

        return DatasetSplit(
            X_train=train.drop(columns=[self.target_column]),
            X_valid=valid.drop(columns=[self.target_column]),
            X_test=test.drop(columns=[self.target_column]),
            y_train=train[self.target_column],
            y_valid=valid[self.target_column],
            y_test=test[self.target_column],
        )

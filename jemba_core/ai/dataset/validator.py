from __future__ import annotations

import pandas as pd


class DatasetValidator:
    REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

    def validate(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("DATASET_EMPTY")

        missing = [
    column
    for column in self.REQUIRED_COLUMNS
    if column not in df.columns
]

        if missing:
            raise ValueError(f"MISSING_COLUMNS: {missing}")

        if df[self.REQUIRED_COLUMNS].isna().any().any():
            raise ValueError("DATASET_CONTAINS_NAN")

        if (df["volume"] < 0).any():
            raise ValueError("NEGATIVE_VOLUME")

        if (df["high"] < df["low"]).any():
            raise ValueError("INVALID_CANDLE_HIGH_LOW")

        if (df["open"] <= 0).any() or (df["high"] <= 0).any():
            raise ValueError("INVALID_PRICE")

        if (df["low"] <= 0).any() or (df["close"] <= 0).any():
            raise ValueError("INVALID_PRICE")

from __future__ import annotations

import pandas as pd


class LabelGenerator:
    def __init__(self, horizon: int = 1):
        self.horizon = horizon

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        if "close" not in data.columns:
            raise ValueError("Missing 'close' column")

        data["future_close"] = data["close"].shift(-self.horizon)
        data["future_return"] = (
            data["future_close"] - data["close"]
        ) / data["close"]

        data["target"] = (data["future_return"] > 0).astype(int)

        return data.dropna(subset=["future_close", "future_return"])

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.transform(df)

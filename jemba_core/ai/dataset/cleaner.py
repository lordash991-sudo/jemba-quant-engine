from __future__ import annotations

import pandas as pd


class DatasetCleaner:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        data = data.drop_duplicates()
        data = data.dropna()

        data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
        data = data.dropna(subset=["timestamp"])

        data = data.sort_values("timestamp")
        data = data.reset_index(drop=True)

        return data

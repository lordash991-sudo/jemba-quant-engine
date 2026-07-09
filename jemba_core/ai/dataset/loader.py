from __future__ import annotations

from pathlib import Path

import pandas as pd


class DatasetLoader:
    def load(self, source: str | Path) -> pd.DataFrame:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)

        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)

        raise ValueError(f"Unsupported dataset format: {path.suffix}")

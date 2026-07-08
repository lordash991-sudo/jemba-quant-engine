from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class Dataset:
    data: pd.DataFrame
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame

    @property
    def rows(self) -> int:
        return len(self.data)

    @property
    def columns(self) -> int:
        return len(self.data.columns)

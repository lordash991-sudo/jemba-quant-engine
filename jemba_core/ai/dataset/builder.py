from __future__ import annotations

from pathlib import Path

from jemba_core.ai.dataset.cleaner import DatasetCleaner
from jemba_core.ai.dataset.loader import DatasetLoader
from jemba_core.ai.dataset.models import Dataset
from jemba_core.ai.dataset.splitter import DatasetSplitter
from jemba_core.ai.dataset.validator import DatasetValidator


class DatasetBuilder:
    def __init__(self):
        self.loader = DatasetLoader()
        self.cleaner = DatasetCleaner()
        self.validator = DatasetValidator()
        self.splitter = DatasetSplitter()

    def build(
        self,
        source: str | Path,
        train_ratio: float = 0.70,
        validation_ratio: float = 0.15,
    ) -> Dataset:
        raw = self.loader.load(source)
        clean = self.cleaner.clean(raw)

        self.validator.validate(clean)

        train, validation, test = self.splitter.split(
            clean,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )

        return Dataset(
            data=clean,
            train=train,
            validation=validation,
            test=test,
        )

from datetime import datetime, timedelta

import pandas as pd
import pytest

from jemba_core.ai.dataset.builder import DatasetBuilder
from jemba_core.ai.dataset.cleaner import DatasetCleaner
from jemba_core.ai.dataset.splitter import DatasetSplitter
from jemba_core.ai.dataset.validator import DatasetValidator


def sample_ohlcv(rows: int = 100) -> pd.DataFrame:
    start = datetime(2024, 1, 1)
    data = []

    for i in range(rows):
        price = 100 + i
        data.append(
            {
                "timestamp": start + timedelta(hours=i),
                "open": price,
                "high": price + 2,
                "low": price - 2,
                "close": price + 1,
                "volume": 1000 + i,
            }
        )

    return pd.DataFrame(data)


def test_dataset_builder_from_csv(tmp_path):
    csv_path = tmp_path / "BTCUSDT_1H.csv"
    sample_ohlcv(100).to_csv(csv_path, index=False)

    dataset = DatasetBuilder().build(csv_path)

    assert dataset.rows == 100
    assert dataset.columns == 6
    assert len(dataset.train) == 70
    assert len(dataset.validation) == 15
    assert len(dataset.test) == 15


def test_validator_rejects_missing_columns():
    df = sample_ohlcv().drop(columns=["volume"])

    with pytest.raises(ValueError, match="MISSING_COLUMNS"):
        DatasetValidator().validate(df)


def test_validator_rejects_negative_volume():
    df = sample_ohlcv()
    df.loc[0, "volume"] = -1

    with pytest.raises(ValueError, match="NEGATIVE_VOLUME"):
        DatasetValidator().validate(df)


def test_cleaner_sorts_and_removes_duplicates():
    df = pd.concat([sample_ohlcv(10), sample_ohlcv(10)])
    df = df.sample(frac=1, random_state=42)

    clean = DatasetCleaner().clean(df)

    assert len(clean) == 10
    assert clean["timestamp"].is_monotonic_increasing


def test_splitter_creates_expected_splits():
    df = sample_ohlcv(100)

    train, validation, test = DatasetSplitter().split(df)

    assert len(train) == 70
    assert len(validation) == 15
    assert len(test) == 15

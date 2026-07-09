from datetime import datetime, timedelta

import pandas as pd

from jemba_core.ai.features.builder import FeatureBuilder
from jemba_core.ai.features.momentum import MomentumFeatures


def sample(rows: int = 300) -> pd.DataFrame:
    start = datetime(2024, 1, 1)
    records = []

    for i in range(rows):
        price = 100 + i
        records.append(
            {
                "timestamp": start + timedelta(hours=i),
                "open": price,
                "high": price + 2,
                "low": price - 2,
                "close": price + 1,
                "volume": 1000,
            }
        )

    return pd.DataFrame(records)


def test_momentum_features_adds_columns():
    df = sample()
    result = MomentumFeatures().transform(df)

    assert "rsi_14" in result.columns
    assert "roc_10" in result.columns
    assert "momentum_5" in result.columns
    assert "momentum_10" in result.columns
    assert "momentum_20" in result.columns


def test_feature_builder_adds_trend_and_momentum():
    df = sample()
    result = FeatureBuilder().transform(df)

    assert "ema_20" in result.columns
    assert "ema_50" in result.columns
    assert "rsi_14" in result.columns
    assert "roc_10" in result.columns
    assert "momentum_10" in result.columns
    assert "macd" in result.columns
    assert "macd_signal" in result.columns
    assert "macd_histogram" in result.columns
    

from datetime import datetime, timedelta

import pandas as pd

from jemba_core.ai.features.builder import FeatureBuilder


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


def test_feature_builder_adds_trend_features():
    df = sample()
    result = FeatureBuilder().transform(df)

    assert "ema_20" in result.columns
    assert "ema_50" in result.columns
    assert "ema_100" in result.columns
    assert "ema_200" in result.columns

    assert "ema20_above_ema50" in result.columns
    assert "ema50_above_ema200" in result.columns

    assert "distance_ema20" in result.columns
    assert "distance_ema50" in result.columns
    assert "distance_ema200" in result.columns

    assert len(result) == len(df)
    assert result["ema_20"].notna().all()

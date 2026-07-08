import pandas as pd

from jemba_core.ai.feature_engineering import FeatureEngineering
from jemba_core.ai.label_generator import LabelGenerator


def sample_ohlcv():
    rows = []
    price = 100

    for i in range(250):
        open_price = price
        close_price = price * (1 + 0.001)
        high = close_price * 1.002
        low = open_price * 0.998
        volume = 1000 + i

        rows.append(
            {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
                "volume": volume,
            }
        )

        price = close_price

    return pd.DataFrame(rows)


def test_feature_engineering_generates_features():
    df = sample_ohlcv()

    result = FeatureEngineering().transform(df)

    assert "ema_20" in result.columns
    assert "ema_50" in result.columns
    assert "ema_200" in result.columns
    assert "atr_14" in result.columns
    assert "volatility_20" in result.columns
    assert len(result) > 0


def test_label_generator_creates_labels():
    df = sample_ohlcv()

    featured = FeatureEngineering().transform(df)
    labeled = LabelGenerator().generate(featured)

    assert "label" in labeled.columns
    assert set(labeled["label"].unique()).issubset({-1, 0, 1})

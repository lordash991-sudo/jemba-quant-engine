from jemba_core.features.feature_engine import FeatureEngine


def test_build_dataframe():
    engine = FeatureEngine()

    candles = [
        {
            "open": "100",
            "high": "110",
            "low": "90",
            "close": "105",
            "volume": "200",
        }
    ]

    df = engine.build(candles)

    assert len(df) == 1
    assert float(df.iloc[0]["close"]) == 105.0


def test_latest():
    engine = FeatureEngine()

    candles = [
        {
            "open": "1",
            "high": "2",
            "low": "0.5",
            "close": "1.5",
            "volume": "100",
        }
    ]

    latest = engine.latest(candles)

    assert latest["close"] == 1.5

from jemba_core.features.feature_engine import FeatureEngine


def sample_candles(n=250):
    candles = []

    for i in range(n):
        price = 100 + i

        candles.append(
            {
                "open": str(price),
                "high": str(price + 5),
                "low": str(price - 5),
                "close": str(price + 2),
                "volume": str(1000 + i),
            }
        )

    return candles


def test_build_dataframe():
    engine = FeatureEngine()

    df = engine.build(sample_candles())

    assert len(df) == 250
    assert float(df.iloc[-1]["close"]) == 351.0


def test_latest():
    engine = FeatureEngine()

    latest = engine.latest(sample_candles())

    assert latest["close"] == 351.0


def test_indicators_exist():
    engine = FeatureEngine()

    df = engine.build(sample_candles())

    expected = [
        "ema_20",
        "ema_50",
        "ema_200",
        "atr_14",
        "rsi_14",
        "return_1",
        "volatility_20",
        "momentum_10",
        "volume_sma_20",
    ]

    for col in expected:
        assert col in df.columns


def test_latest_indicators_not_empty():
    engine = FeatureEngine()

    latest = engine.latest(sample_candles())

    assert latest["ema_20"] is not None
    assert latest["ema_50"] is not None
    assert latest["ema_200"] is not None
    assert latest["atr_14"] is not None
    assert latest["rsi_14"] is not None

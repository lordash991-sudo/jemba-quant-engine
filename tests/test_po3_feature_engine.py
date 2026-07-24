from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from jemba_core.features.po3_feature_engine import (
    PO3FeatureConfig,
    PO3FeatureEngine,
)


def make_market(rows: int = 600) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    timestamp = pd.date_range(
        "2025-01-01",
        periods=rows,
        freq="h",
        tz="UTC",
    )

    returns = rng.normal(
        loc=0.0001,
        scale=0.006,
        size=rows,
    )

    close = 60_000.0 * np.exp(
        np.cumsum(returns)
    )

    open_price = np.concatenate(
        ([close[0]], close[:-1])
    )

    spread = np.maximum(
        close * rng.uniform(
            0.001,
            0.008,
            size=rows,
        ),
        1.0,
    )

    high = np.maximum(
        open_price,
        close,
    ) + spread

    low = np.minimum(
        open_price,
        close,
    ) - spread

    volume = rng.uniform(
        100.0,
        1_000.0,
        size=rows,
    )

    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def test_build_generates_all_output_features() -> None:
    engine = PO3FeatureEngine()
    result = engine.build(make_market())

    missing = [
        feature
        for feature in engine.OUTPUT_FEATURES
        if feature not in result.columns
    ]

    assert missing == []
    assert len(result) == 600


def test_feature_matrix_has_exact_feature_order() -> None:
    engine = PO3FeatureEngine()
    matrix = engine.feature_matrix(make_market())

    assert list(matrix.columns) == list(
        engine.OUTPUT_FEATURES
    )

    assert not matrix.empty
    assert not matrix.isna().any().any()


def test_latest_returns_single_row() -> None:
    engine = PO3FeatureEngine()
    latest = engine.latest(make_market())

    assert len(latest) == 1
    assert list(latest.columns) == list(
        engine.OUTPUT_FEATURES
    )


def test_invalid_market_raises_error() -> None:
    engine = PO3FeatureEngine()

    with pytest.raises(
        ValueError,
        match="MISSING_OHLCV_COLUMNS",
    ):
        engine.build(
            pd.DataFrame(
                {
                    "close": [100.0],
                }
            )
        )


def test_invalid_breakout_method_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="BREAKOUT_METHOD_MUST_BE_WICK_OR_CLOSE",
    ):
        PO3FeatureConfig(
            breakout_method="invalid",
        )


def test_signal_values_are_valid() -> None:
    engine = PO3FeatureEngine()
    result = engine.build(make_market())

    valid_signals = {-1, 0, 1}

    assert set(
        result["PO3_SIGNAL"]
        .dropna()
        .astype(int)
        .unique()
    ).issubset(valid_signals)


def test_no_future_data_is_required() -> None:
    engine = PO3FeatureEngine()

    complete = make_market(600)

    first_result = engine.build(
        complete.iloc[:500].copy()
    )

    second_result = engine.build(
        complete.copy()
    ).iloc[:500]

    comparable_columns = [
        column
        for column in engine.OUTPUT_FEATURES
        if column not in {
            "MANIPULATION_DIRECTION",
        }
    ]

    pd.testing.assert_frame_equal(
        first_result[comparable_columns],
        second_result[comparable_columns],
        check_dtype=False,
        check_exact=False,
        rtol=1e-10,
        atol=1e-10,
    )


def test_sparse_event_features_use_zero_when_event_is_absent() -> None:
    engine = PO3FeatureEngine()
    matrix = engine.feature_matrix(make_market())

    sparse_event_features = [
        "MANIPULATION_DISTANCE",
        "MANIPULATION_ATR",
        "BREAKOUT_FORCE",
        "DISTRIBUTION_BODY_ATR",
        "DISTRIBUTION_RANGE_ATR",
    ]

    assert not matrix.empty

    assert not (
        matrix[sparse_event_features]
        .isna()
        .any()
        .any()
    )

    assert (
        matrix[sparse_event_features]
        .ge(0.0)
        .all()
        .all()
    )


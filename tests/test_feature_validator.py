from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from jemba_core.ai.inference import FeatureValidator


def test_validates_numeric_list():
    validator = FeatureValidator(expected_features=2)

    result = validator.validate([[1, 2], [3, 4]])

    assert result.shape == (2, 2)
    assert result.dtype == float


def test_validates_numpy_array():
    validator = FeatureValidator(expected_features=3)

    result = validator.validate(np.array([[1.0, 2.0, 3.0]]))

    assert result.shape == (1, 3)


def test_validates_dataframe_columns():
    validator = FeatureValidator(
        expected_columns=["rsi", "atr"],
        expected_features=2,
    )

    frame = pd.DataFrame(
        {
            "rsi": [55.0],
            "atr": [120.0],
        }
    )

    result = validator.validate_frame(frame)

    assert result.shape == (1, 2)


def test_rejects_wrong_dataframe_columns():
    validator = FeatureValidator(expected_columns=["rsi", "atr"])

    frame = pd.DataFrame(
        {
            "atr": [120.0],
            "rsi": [55.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="FEATURE_COLUMNS_MISMATCH",
    ):
        validator.validate_frame(frame)


def test_rejects_empty_features():
    validator = FeatureValidator()

    with pytest.raises(
        ValueError,
        match="FEATURES_CANNOT_BE_EMPTY",
    ):
        validator.validate(np.empty((0, 2)))


def test_rejects_zero_columns():
    validator = FeatureValidator()

    with pytest.raises(
        ValueError,
        match="FEATURES_CANNOT_HAVE_ZERO_COLUMNS",
    ):
        validator.validate(np.empty((1, 0)))


def test_rejects_one_dimensional_input():
    validator = FeatureValidator()

    with pytest.raises(
        ValueError,
        match="FEATURES_MUST_BE_2D",
    ):
        validator.validate([1.0, 2.0])


def test_rejects_wrong_feature_count():
    validator = FeatureValidator(expected_features=3)

    with pytest.raises(
        ValueError,
        match="FEATURE_COUNT_MISMATCH",
    ):
        validator.validate([[1.0, 2.0]])


def test_rejects_nan():
    validator = FeatureValidator()

    with pytest.raises(
        ValueError,
        match="FEATURES_CONTAIN_NAN",
    ):
        validator.validate([[1.0, np.nan]])


def test_rejects_infinity():
    validator = FeatureValidator()

    with pytest.raises(
        ValueError,
        match="FEATURES_CONTAIN_INFINITY",
    ):
        validator.validate([[1.0, np.inf]])


def test_rejects_non_numeric_values():
    validator = FeatureValidator()

    with pytest.raises(
        TypeError,
        match="FEATURES_MUST_BE_NUMERIC",
    ):
        validator.validate([["abc", "def"]])


def test_allows_empty_when_configured():
    validator = FeatureValidator(
        expected_features=2,
        allow_empty=True,
    )

    result = validator.validate(np.empty((0, 2)))

    assert result.shape == (0, 2)


def test_rejects_invalid_expected_feature_count():
    with pytest.raises(
        ValueError,
        match="EXPECTED_FEATURES_MUST_BE_POSITIVE",
    ):
        FeatureValidator(expected_features=0)

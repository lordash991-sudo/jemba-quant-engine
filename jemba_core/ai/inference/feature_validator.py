from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd


class FeatureValidator:
    def __init__(
        self,
        *,
        expected_columns: Sequence[str] | None = None,
        expected_features: int | None = None,
        allow_empty: bool = False,
    ) -> None:
        if expected_features is not None and expected_features <= 0:
            raise ValueError("EXPECTED_FEATURES_MUST_BE_POSITIVE")

        self.expected_columns = (
            list(expected_columns) if expected_columns is not None else None
        )
        self.expected_features = expected_features
        self.allow_empty = allow_empty

    def validate(
        self,
        features: Any,
    ) -> np.ndarray:
        array = self._to_array(features)

        if array.ndim != 2:
            raise ValueError(f"FEATURES_MUST_BE_2D: ndim={array.ndim}")

        rows, columns = array.shape

        if rows == 0 and not self.allow_empty:
            raise ValueError("FEATURES_CANNOT_BE_EMPTY")

        if columns == 0:
            raise ValueError("FEATURES_CANNOT_HAVE_ZERO_COLUMNS")

        if self.expected_features is not None and columns != self.expected_features:
            raise ValueError(
                "FEATURE_COUNT_MISMATCH: "
                f"expected={self.expected_features}, "
                f"received={columns}"
            )

        if not np.issubdtype(array.dtype, np.number):
            raise TypeError("FEATURES_MUST_BE_NUMERIC")

        numeric = array.astype(float, copy=False)

        if np.isnan(numeric).any():
            raise ValueError("FEATURES_CONTAIN_NAN")

        if np.isinf(numeric).any():
            raise ValueError("FEATURES_CONTAIN_INFINITY")

        return numeric

    def validate_frame(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("FEATURES_MUST_BE_DATAFRAME")

        if self.expected_columns is not None:
            received_columns = list(frame.columns)

            if received_columns != self.expected_columns:
                raise ValueError(
                    "FEATURE_COLUMNS_MISMATCH: "
                    f"expected={self.expected_columns}, "
                    f"received={received_columns}"
                )

        return self.validate(frame)

    def _to_array(
        self,
        features: Any,
    ) -> np.ndarray:
        if isinstance(features, pd.DataFrame):
            if self.expected_columns is not None:
                return self.validate_frame(features)

            return features.to_numpy()

        try:
            return np.asarray(features)
        except Exception as exc:
            raise TypeError("FEATURES_CANNOT_BE_CONVERTED_TO_ARRAY") from exc

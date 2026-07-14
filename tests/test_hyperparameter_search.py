from __future__ import annotations

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, TimeSeriesSplit

from jemba_core.ai.hyperparameter_search import (
    HyperparameterSearch,
)
from jemba_core.ai.search_result import SearchResult


def make_dataset():
    rng = np.random.default_rng(42)

    X = rng.normal(size=(80, 4))
    y = (X[:, 0] + X[:, 1] * 0.5 - X[:, 2] * 0.25 > 0).astype(int)

    return X, y


def test_randomized_search_returns_typed_result():
    X, y = make_dataset()

    search = HyperparameterSearch(
        strategy="randomized",
        cv_strategy="timeseries",
        scoring="f1",
        n_splits=3,
        n_iter=2,
        n_jobs=1,
    )

    result = search.run(
        estimator=RandomForestClassifier(random_state=42),
        param_space={
            "n_estimators": [5, 10],
            "max_depth": [2, 3],
        },
        X=X,
        y=y,
    )

    assert isinstance(result, SearchResult)
    assert result.best_estimator is not None
    assert result.best_params
    assert isinstance(result.best_score, float)
    assert result.strategy == "randomized"
    assert result.cv_strategy == "timeseries"
    assert "mean_test_score" in result.cv_results


def test_grid_search_finds_best_parameters():
    X, y = make_dataset()

    search = HyperparameterSearch(
        strategy="grid",
        cv_strategy="kfold",
        scoring="accuracy",
        n_splits=3,
        n_jobs=1,
    )

    result = search.run(
        estimator=LogisticRegression(
            max_iter=500,
            random_state=42,
        ),
        param_space={
            "C": [0.1, 1.0],
        },
        X=X,
        y=y,
    )

    assert result.best_params["C"] in {
        0.1,
        1.0,
    }
    assert result.strategy == "grid"
    assert result.cv_strategy == "kfold"
    assert 0.0 <= result.best_score <= 1.0


def test_builds_time_series_split_by_default():
    search = HyperparameterSearch(n_splits=4)

    cv = search._build_cv()

    assert isinstance(cv, TimeSeriesSplit)
    assert cv.n_splits == 4


def test_builds_kfold_when_requested():
    search = HyperparameterSearch(
        cv_strategy="kfold",
        n_splits=4,
    )

    cv = search._build_cv()

    assert isinstance(cv, KFold)
    assert cv.n_splits == 4
    assert cv.shuffle is True


def test_rejects_invalid_search_strategy():
    with pytest.raises(
        ValueError,
        match="INVALID_SEARCH_STRATEGY",
    ):
        HyperparameterSearch(
            strategy="invented",
        )


def test_rejects_invalid_cv_strategy():
    with pytest.raises(
        ValueError,
        match="INVALID_CV_STRATEGY",
    ):
        HyperparameterSearch(
            cv_strategy="future_leakage",
        )


def test_rejects_invalid_split_count():
    with pytest.raises(
        ValueError,
        match="N_SPLITS_MUST_BE_AT_LEAST_TWO",
    ):
        HyperparameterSearch(n_splits=1)


def test_rejects_invalid_iteration_count():
    with pytest.raises(
        ValueError,
        match="N_ITER_MUST_BE_POSITIVE",
    ):
        HyperparameterSearch(n_iter=0)


def test_requires_estimator():
    X, y = make_dataset()
    search = HyperparameterSearch(n_splits=3)

    with pytest.raises(
        ValueError,
        match="ESTIMATOR_IS_REQUIRED",
    ):
        search.run(
            estimator=None,
            param_space={"x": [1]},
            X=X,
            y=y,
        )


def test_rejects_empty_parameter_space():
    X, y = make_dataset()
    search = HyperparameterSearch(n_splits=3)

    with pytest.raises(
        ValueError,
        match="PARAM_SPACE_CANNOT_BE_EMPTY",
    ):
        search.run(
            estimator=RandomForestClassifier(random_state=42),
            param_space={},
            X=X,
            y=y,
        )

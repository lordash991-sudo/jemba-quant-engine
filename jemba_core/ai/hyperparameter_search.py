from __future__ import annotations

from typing import Any, Literal

from sklearn.model_selection import (
    GridSearchCV,
    KFold,
    RandomizedSearchCV,
    TimeSeriesSplit,
)

from jemba_core.ai.search_result import SearchResult

SearchStrategy = Literal["randomized", "grid"]
CVStrategy = Literal["timeseries", "kfold"]


class HyperparameterSearch:
    def __init__(
        self,
        *,
        strategy: SearchStrategy = "randomized",
        cv_strategy: CVStrategy = "timeseries",
        scoring: str | None = "f1",
        n_splits: int = 5,
        n_iter: int = 20,
        random_state: int = 42,
        n_jobs: int = -1,
        verbose: int = 0,
    ) -> None:
        if strategy not in {"randomized", "grid"}:
            raise ValueError(f"INVALID_SEARCH_STRATEGY: {strategy}")

        if cv_strategy not in {"timeseries", "kfold"}:
            raise ValueError(f"INVALID_CV_STRATEGY: {cv_strategy}")

        if n_splits < 2:
            raise ValueError("N_SPLITS_MUST_BE_AT_LEAST_TWO")

        if n_iter <= 0:
            raise ValueError("N_ITER_MUST_BE_POSITIVE")

        self.strategy = strategy
        self.cv_strategy = cv_strategy
        self.scoring = scoring
        self.n_splits = n_splits
        self.n_iter = n_iter
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.verbose = verbose

    def run(
        self,
        *,
        estimator: Any,
        param_space: dict[str, Any],
        X: Any,
        y: Any,
    ) -> SearchResult:
        if estimator is None:
            raise ValueError("ESTIMATOR_IS_REQUIRED")

        if not param_space:
            raise ValueError("PARAM_SPACE_CANNOT_BE_EMPTY")

        cv = self._build_cv()
        search = self._build_search(
            estimator=estimator,
            param_space=param_space,
            cv=cv,
        )

        search.fit(X, y)

        return SearchResult(
            best_estimator=search.best_estimator_,
            best_params=dict(search.best_params_),
            best_score=float(search.best_score_),
            cv_results=dict(search.cv_results_),
            strategy=self.strategy,
            cv_strategy=self.cv_strategy,
            scoring=self.scoring,
        )

    def _build_cv(
        self,
    ) -> TimeSeriesSplit | KFold:
        if self.cv_strategy == "timeseries":
            return TimeSeriesSplit(n_splits=self.n_splits)

        return KFold(
            n_splits=self.n_splits,
            shuffle=True,
            random_state=self.random_state,
        )

    def _build_search(
        self,
        *,
        estimator: Any,
        param_space: dict[str, Any],
        cv: TimeSeriesSplit | KFold,
    ) -> RandomizedSearchCV | GridSearchCV:
        common_options = {
            "estimator": estimator,
            "scoring": self.scoring,
            "cv": cv,
            "n_jobs": self.n_jobs,
            "verbose": self.verbose,
            "refit": True,
            "error_score": "raise",
            "return_train_score": True,
        }

        if self.strategy == "randomized":
            return RandomizedSearchCV(
                param_distributions=param_space,
                n_iter=self.n_iter,
                random_state=self.random_state,
                **common_options,
            )

        return GridSearchCV(
            param_grid=param_space,
            **common_options,
        )

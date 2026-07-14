from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from jemba_core.ai.ensemble_trainer import (
    EnsembleResult,
    EnsembleTrainer,
)


def dataset():

    rng = np.random.default_rng(42)

    X = rng.normal(size=(120, 4))

    y = (X[:, 0] + X[:, 1] - X[:, 2] > 0).astype(int)

    return (
        X[:80],
        y[:80],
        X[80:],
        y[80:],
    )


def test_selects_best_model():

    X_train, y_train, X_valid, y_valid = dataset()

    trainer = EnsembleTrainer()

    result = trainer.train(
        models={
            "rf": RandomForestClassifier(
                random_state=42,
                n_estimators=20,
            ),
            "lr": LogisticRegression(
                max_iter=500,
            ),
        },
        X_train=X_train,
        y_train=y_train,
        X_valid=X_valid,
        y_valid=y_valid,
    )

    assert isinstance(result, EnsembleResult)

    assert result.best_name in {
        "rf",
        "lr",
    }

    assert result.best_model is not None

    assert len(result.scores) == 2


def test_empty_models():

    X_train, y_train, X_valid, y_valid = dataset()

    trainer = EnsembleTrainer()

    import pytest

    with pytest.raises(
        ValueError,
        match="NO_MODELS_PROVIDED",
    ):
        trainer.train(
            models={},
            X_train=X_train,
            y_train=y_train,
            X_valid=X_valid,
            y_valid=y_valid,
        )

from __future__ import annotations

from dataclasses import dataclass

from sklearn.base import clone

from jemba_core.ai.model_evaluator import ModelEvaluator


@dataclass(slots=True)
class EnsembleResult:
    best_name: str
    best_model: object
    scores: dict[str, float]


class EnsembleTrainer:
    def __init__(
        self,
        *,
        evaluator: ModelEvaluator | None = None,
    ):
        self.evaluator = evaluator or ModelEvaluator()

    def train(
        self,
        *,
        models: dict,
        X_train,
        y_train,
        X_valid,
        y_valid,
    ) -> EnsembleResult:

        if not models:
            raise ValueError("NO_MODELS_PROVIDED")

        scores = {}

        best_name = None
        best_model = None
        best_score = -1.0

        for name, estimator in models.items():
            model = clone(estimator)

            model.fit(X_train, y_train)

            prediction = model.predict(X_valid)

            metrics = self.evaluator.evaluate(
                y_true=y_valid,
                y_pred=prediction,
            )

            score = metrics.f1

            scores[name] = score

            if score > best_score:
                best_score = score
                best_name = name
                best_model = model

        return EnsembleResult(
            best_name=best_name,
            best_model=best_model,
            scores=scores,
        )

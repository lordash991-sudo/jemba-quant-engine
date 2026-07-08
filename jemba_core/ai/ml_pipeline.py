from sklearn.model_selection import train_test_split

from jemba_core.ai.metrics import Metrics
from jemba_core.ai.model_registry import ModelRegistry
from jemba_core.ai.training_result import TrainingResult


class MLPipeline:

    def train(
        self,
        df,
        target="label",
        model="random_forest",
    ):

        X = df.drop(columns=[target])

        y = df[target]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            shuffle=False,
            test_size=0.25,
        )

        estimator = ModelRegistry.get(model)

        estimator.fit(X_train, y_train)

        prediction = estimator.predict(X_test)

        metric = Metrics.evaluate(
            y_test,
            prediction,
        )

        return estimator, TrainingResult(
            model_name=model,
            accuracy=metric["accuracy"],
            precision=metric["precision"],
            recall=metric["recall"],
            f1=metric["f1"],
        )

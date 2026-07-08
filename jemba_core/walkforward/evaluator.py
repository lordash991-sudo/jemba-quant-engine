from .optimizer import WalkForwardOptimizer


class WalkForwardEvaluator:
    def __init__(
        self,
        scoring_function,
    ):
        self.optimizer = WalkForwardOptimizer(
            scoring_function,
        )

    def evaluate(
        self,
        train_data,
        test_data,
        parameter_grid,
    ):
        train_score, params = self.optimizer.optimize(
            train_data,
            parameter_grid,
        )

        test_score = self.optimizer.scoring_function(
            test_data,
            params,
        )

        return self.optimizer.build_result(
            train_score,
            test_score,
            params,
        )
from .models import WalkForwardResult


class WalkForwardOptimizer:
    def __init__(self, scoring_function):
        self.scoring_function = scoring_function

    def optimize(
        self,
        train_data,
        parameter_grid,
    ):
        best_score = float("-inf")
        best_params = None

        for params in parameter_grid:
            score = self.scoring_function(
                train_data,
                params,
            )

            if score > best_score:
                best_score = score
                best_params = params

        return best_score, best_params

    def build_result(
        self,
        train_score,
        test_score,
        parameters,
    ):
        return WalkForwardResult(
            train_score=train_score,
            test_score=test_score,
            parameters=parameters,
        )

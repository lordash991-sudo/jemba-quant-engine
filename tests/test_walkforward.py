from jemba_core.walkforward.evaluator import WalkForwardEvaluator
from jemba_core.walkforward.splitter import WalkForwardSplitter


def fake_score(data, params):
    return sum(data) * params["weight"]


def test_splitter():
    splitter = WalkForwardSplitter(
        train_size=60,
        test_size=20,
        step=20,
    )

    windows = splitter.split(200)

    assert len(windows) == 7
    assert windows[0].train_start == 0
    assert windows[0].train_end == 60
    assert windows[0].test_start == 60
    assert windows[0].test_end == 80


def test_optimizer():
    evaluator = WalkForwardEvaluator(fake_score)

    result = evaluator.evaluate(
        train_data=[1, 2, 3],
        test_data=[4, 5],
        parameter_grid=[
            {"weight": 1},
            {"weight": 2},
            {"weight": 3},
        ],
    )

    assert result.train_score == 18
    assert result.test_score == 27

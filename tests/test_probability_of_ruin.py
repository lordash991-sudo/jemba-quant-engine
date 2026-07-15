from jemba_core.montecarlo.probability_of_ruin import probability_of_ruin


def test_probability_between_zero_and_one():
    value = probability_of_ruin(
        win_rate=0.58,
        payoff_ratio=1.4,
        risk_per_trade=0.01,
        ruin_threshold=0.50,
    )

    assert 0 <= value <= 1


def test_negative_edge_returns_one():
    value = probability_of_ruin(
        win_rate=0.30,
        payoff_ratio=0.8,
        risk_per_trade=0.01,
        ruin_threshold=0.50,
    )

    assert value == 1.0

import numpy as np

from jemba_core.montecarlo import MonteCarloResult


def test_result_exposes_profit_properties():
    result = MonteCarloResult(
        simulations=2,
        initial_balance=1000.0,
        mean_final_equity=1100.0,
        median_final_equity=1100.0,
        standard_deviation=10.0,
        best_case=1150.0,
        worst_case=1050.0,
        percentile_5=1055.0,
        percentile_95=1145.0,
        confidence_interval_95=(1055.0, 1145.0),
        mean_max_drawdown=0.10,
        worst_max_drawdown=0.20,
        final_equities=np.array([1050.0, 1150.0]),
        max_drawdowns=np.array([0.10, 0.20]),
        equity_curves=np.array(
            [
                [1000.0, 1050.0],
                [1000.0, 1150.0],
            ]
        ),
    )

    assert result.mean_net_profit == 100.0
    assert result.worst_net_profit == 50.0
    assert result.best_net_profit == 150.0
    assert result.to_dict()["simulations"] == 2

import numpy as np
import pytest

from jemba_core.montecarlo import Simulation


def test_builds_simulation_from_trades():
    simulation = Simulation.from_trades(
        np.array([100.0, -50.0, 25.0]),
        initial_balance=1000.0,
    )

    np.testing.assert_allclose(
        simulation.equity_curve,
        [1000.0, 1100.0, 1050.0, 1075.0],
    )

    assert simulation.final_equity == 1075.0
    assert simulation.net_profit == 75.0
    assert simulation.max_drawdown > 0.0


def test_rejects_non_finite_trades():
    with pytest.raises(
        ValueError,
        match="TRADES_MUST_BE_FINITE",
    ):
        Simulation.from_trades(
            np.array([10.0, np.nan]),
            initial_balance=1000.0,
        )

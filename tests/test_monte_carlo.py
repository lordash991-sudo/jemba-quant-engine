import numpy as np
import pytest

from jemba_core.montecarlo import (
    MonteCarloResult,
    MonteCarloSimulator,
)


def test_runs_reproducible_shuffle_simulation():
    trades = [100.0, -50.0, 25.0, -10.0]

    first = MonteCarloSimulator(
        trades,
        simulations=20,
        initial_balance=1000.0,
        seed=42,
    ).run()

    second = MonteCarloSimulator(
        trades,
        simulations=20,
        initial_balance=1000.0,
        seed=42,
    ).run()

    np.testing.assert_allclose(
        first.equity_curves,
        second.equity_curves,
    )

    assert isinstance(first, MonteCarloResult)
    assert first.simulations == 20


def test_bootstrap_produces_variable_final_equity():
    result = MonteCarloSimulator(
        [100.0, -50.0, 25.0, -10.0],
        simulations=100,
        initial_balance=1000.0,
        seed=42,
        sampling="bootstrap",
    ).run()

    assert np.unique(result.final_equities).size > 1
    assert result.best_case >= result.worst_case
    assert result.worst_max_drawdown >= 0.0


def test_shuffle_preserves_total_profit():
    trades = [100.0, -50.0, 25.0]

    result = MonteCarloSimulator(
        trades,
        simulations=30,
        initial_balance=1000.0,
        seed=42,
        sampling="shuffle",
    ).run()

    np.testing.assert_allclose(
        result.final_equities,
        1075.0,
    )


def test_rejects_empty_trades():
    with pytest.raises(
        ValueError,
        match="TRADES_CANNOT_BE_EMPTY",
    ):
        MonteCarloSimulator([])


def test_rejects_invalid_sampling():
    with pytest.raises(
        ValueError,
        match="INVALID_SAMPLING_METHOD",
    ):
        MonteCarloSimulator(
            [10.0, -5.0],
            sampling="telepathy",
        )

from jemba_core.backtest.trade import Trade
from jemba_core.montecarlo.engine import MonteCarloEngine


def sample_trades():
    return [
        Trade("BTC", "LONG", 100, 105, 1, 100, 5),
        Trade("BTC", "LONG", 105, 103, 1, -50, -2),
        Trade("BTC", "SHORT", 103, 99, 1, 120, 4),
        Trade("ETH", "LONG", 200, 210, 1, 80, 4),
        Trade("SOL", "SHORT", 50, 48, 1, -40, -3),
    ]


def test_montecarlo_engine_runs():
    engine = MonteCarloEngine(simulations=100, seed=42)

    result = engine.run(
        sample_trades(),
        initial_balance=10000,
    )

    assert result.simulations == 100
    assert result.initial_balance == 10000
    assert result.mean_final_balance > 0
    assert result.worst_max_drawdown >= 0
    assert 0 <= result.risk_of_ruin <= 1


def test_montecarlo_empty_trades():
    engine = MonteCarloEngine(simulations=100)

    result = engine.run([], initial_balance=10000)

    assert result.mean_final_balance == 10000
    assert result.risk_of_ruin == 0.0

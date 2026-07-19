import pytest

from jemba_core.montecarlo.monte_carlo_engine import (
    MonteCarloConfig,
    MonteCarloEngine,
    SamplingMode,
)

TRADE_RETURNS = [
    0.02,
    -0.01,
    0.03,
    -0.02,
    0.015,
]


def test_generates_requested_number_of_simulations():
    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=25,
            seed=7,
        )
    )

    result = engine.run(TRADE_RETURNS)

    assert len(result.paths) == 25
    assert len(result.final_equities) == 25
    assert len(result.max_drawdowns) == 25


def test_seed_makes_bootstrap_reproducible():
    config = MonteCarloConfig(
        simulations=20,
        seed=42,
    )

    first = MonteCarloEngine(config).run(TRADE_RETURNS)
    second = MonteCarloEngine(config).run(TRADE_RETURNS)

    assert first.paths == second.paths


def test_different_seeds_can_produce_different_results():
    first = MonteCarloEngine(
        MonteCarloConfig(
            simulations=20,
            seed=1,
        )
    ).run(TRADE_RETURNS)

    second = MonteCarloEngine(
        MonteCarloConfig(
            simulations=20,
            seed=2,
        )
    ).run(TRADE_RETURNS)

    assert first.final_equities != second.final_equities


def test_shuffle_preserves_final_compounded_equity():
    config = MonteCarloConfig(
        simulations=10,
        initial_equity=1_000,
        sampling_mode=SamplingMode.SHUFFLE,
        seed=21,
    )

    result = MonteCarloEngine(config).run(TRADE_RETURNS)

    expected = 1_000

    for trade_return in TRADE_RETURNS:
        expected *= 1 + trade_return

    for final_equity in result.final_equities:
        assert final_equity == pytest.approx(expected)


def test_can_store_equity_curves():
    config = MonteCarloConfig(
        simulations=3,
        sample_size=8,
        seed=5,
        store_equity_curves=True,
    )

    result = MonteCarloEngine(config).run(TRADE_RETURNS)

    for path in result.paths:
        assert path.equity_curve is not None
        assert len(path.equity_curve) == 9


def test_does_not_store_curves_by_default():
    result = MonteCarloEngine(
        MonteCarloConfig(
            simulations=2,
            seed=4,
        )
    ).run(TRADE_RETURNS)

    assert all(path.equity_curve is None for path in result.paths)


def test_reports_aggregate_metrics():
    result = MonteCarloEngine(
        MonteCarloConfig(
            simulations=50,
            seed=11,
        )
    ).run(TRADE_RETURNS)

    assert result.mean_final_equity > 0
    assert result.median_final_equity > 0
    assert result.worst_final_equity <= result.best_final_equity
    assert 0 <= result.worst_max_drawdown <= 1
    assert 0 <= result.probability_of_loss <= 1


def test_reports_percentiles():
    result = MonteCarloEngine(
        MonteCarloConfig(
            simulations=50,
            seed=15,
        )
    ).run(TRADE_RETURNS)

    percentile_5 = result.percentile_final_equity(5)
    percentile_95 = result.percentile_final_equity(95)

    assert percentile_5 <= percentile_95
    assert result.percentile_max_drawdown(95) >= 0


def test_rejects_empty_returns():
    engine = MonteCarloEngine()

    with pytest.raises(
        ValueError,
        match="TRADE_RETURNS_CANNOT_BE_EMPTY",
    ):
        engine.run([])


def test_rejects_total_loss_or_worse():
    engine = MonteCarloEngine()

    with pytest.raises(
        ValueError,
        match="TRADE_RETURN_MUST_BE_GREATER_THAN_MINUS_ONE",
    ):
        engine.run([0.10, -1.0])


def test_rejects_invalid_simulation_count():
    with pytest.raises(
        ValueError,
        match="SIMULATIONS_MUST_BE_POSITIVE",
    ):
        MonteCarloConfig(simulations=0)


def test_rejects_invalid_shuffle_sample_size():
    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=5,
            sample_size=3,
            sampling_mode=SamplingMode.SHUFFLE,
        )
    )

    with pytest.raises(
        ValueError,
        match="SHUFFLE_SAMPLE_SIZE_MUST_MATCH_RETURNS_LENGTH",
    ):
        engine.run(TRADE_RETURNS)


def test_rejects_invalid_percentile():
    result = MonteCarloEngine(
        MonteCarloConfig(
            simulations=5,
            seed=10,
        )
    ).run(TRADE_RETURNS)

    with pytest.raises(
        ValueError,
        match="PERCENTILE_MUST_BE_BETWEEN_0_AND_100",
    ):
        result.percentile_final_equity(101)

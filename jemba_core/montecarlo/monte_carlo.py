from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray

from jemba_core.montecarlo.monte_carlo_result import (
    MonteCarloResult,
)
from jemba_core.montecarlo.simulation import Simulation
from jemba_core.montecarlo.statistics import (
    confidence_interval,
    mean,
    median,
    percentile,
    standard_deviation,
)


class MonteCarloSimulator:
    def __init__(
        self,
        trades: Iterable[float],
        *,
        simulations: int = 1000,
        initial_balance: float = 10_000.0,
        seed: int | None = None,
        sampling: str = "shuffle",
    ) -> None:
        values = np.asarray(list(trades), dtype=float)

        if values.ndim != 1:
            raise ValueError("TRADES_MUST_BE_ONE_DIMENSIONAL")

        if values.size == 0:
            raise ValueError("TRADES_CANNOT_BE_EMPTY")

        if not np.isfinite(values).all():
            raise ValueError("TRADES_MUST_BE_FINITE")

        if simulations <= 0:
            raise ValueError("SIMULATIONS_MUST_BE_POSITIVE")

        if not np.isfinite(initial_balance):
            raise ValueError("INITIAL_BALANCE_MUST_BE_FINITE")

        if sampling not in {"shuffle", "bootstrap"}:
            raise ValueError(f"INVALID_SAMPLING_METHOD: {sampling}")

        self.trades = values
        self.simulations = simulations
        self.initial_balance = float(initial_balance)
        self.seed = seed
        self.sampling = sampling

    def run(self) -> MonteCarloResult:
        random = np.random.default_rng(self.seed)

        final_equities = np.empty(
            self.simulations,
            dtype=float,
        )
        max_drawdowns = np.empty(
            self.simulations,
            dtype=float,
        )
        equity_curves = np.empty(
            (
                self.simulations,
                self.trades.size + 1,
            ),
            dtype=float,
        )

        for index in range(self.simulations):
            sampled_trades = self._sample(random)

            simulation = Simulation.from_trades(
                sampled_trades,
                initial_balance=self.initial_balance,
            )

            final_equities[index] = simulation.final_equity
            max_drawdowns[index] = simulation.max_drawdown
            equity_curves[index] = simulation.equity_curve

        return MonteCarloResult(
            simulations=self.simulations,
            initial_balance=self.initial_balance,
            mean_final_equity=mean(final_equities),
            median_final_equity=median(final_equities),
            standard_deviation=standard_deviation(final_equities),
            best_case=float(np.max(final_equities)),
            worst_case=float(np.min(final_equities)),
            percentile_5=percentile(final_equities, 5.0),
            percentile_95=percentile(final_equities, 95.0),
            confidence_interval_95=confidence_interval(
                final_equities,
                confidence=0.95,
            ),
            mean_max_drawdown=mean(max_drawdowns),
            worst_max_drawdown=float(np.max(max_drawdowns)),
            final_equities=final_equities,
            max_drawdowns=max_drawdowns,
            equity_curves=equity_curves,
        )

    def _sample(
        self,
        random: np.random.Generator,
    ) -> NDArray[np.float64]:
        if self.sampling == "bootstrap":
            return random.choice(
                self.trades,
                size=self.trades.size,
                replace=True,
            )

        return random.permutation(self.trades)

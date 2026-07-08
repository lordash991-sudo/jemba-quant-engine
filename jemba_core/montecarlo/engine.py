from __future__ import annotations

import random

from jemba_core.backtest.metrics import Metrics
from jemba_core.montecarlo.models import MonteCarloResult


class MonteCarloEngine:
    def __init__(
        self,
        simulations: int = 1000,
        ruin_threshold: float = 0.30,
        seed: int = 42,
    ):
        self.simulations = simulations
        self.ruin_threshold = ruin_threshold
        self.seed = seed

    def run(
        self,
        trades,
        initial_balance: float = 10000,
    ) -> MonteCarloResult:
        if not trades:
            return MonteCarloResult(
                simulations=self.simulations,
                initial_balance=initial_balance,
                mean_final_balance=initial_balance,
                worst_final_balance=initial_balance,
                best_final_balance=initial_balance,
                mean_max_drawdown=0.0,
                worst_max_drawdown=0.0,
                risk_of_ruin=0.0,
            )

        rng = random.Random(self.seed)

        final_balances = []
        max_drawdowns = []
        ruins = 0

        ruin_balance = initial_balance * (1 - self.ruin_threshold)

        for _ in range(self.simulations):
            shuffled = list(trades)
            rng.shuffle(shuffled)

            balance = initial_balance
            equity = [balance]

            for trade in shuffled:
                balance += trade.pnl
                equity.append(balance)

            final_balance = equity[-1]
            max_drawdown = Metrics.max_drawdown(equity)

            final_balances.append(final_balance)
            max_drawdowns.append(max_drawdown)

            if min(equity) <= ruin_balance:
                ruins += 1

        return MonteCarloResult(
            simulations=self.simulations,
            initial_balance=initial_balance,
            mean_final_balance=sum(final_balances) / len(final_balances),
            worst_final_balance=min(final_balances),
            best_final_balance=max(final_balances),
            mean_max_drawdown=sum(max_drawdowns) / len(max_drawdowns),
            worst_max_drawdown=max(max_drawdowns),
            risk_of_ruin=ruins / self.simulations,
        )

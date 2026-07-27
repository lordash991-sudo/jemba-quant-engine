from __future__ import annotations

from collections.abc import Iterable

from jemba_core.lab.models import BacktestMetrics


class AssetRanker:
    def rank(
        self,
        results: Iterable[BacktestMetrics],
    ) -> list[BacktestMetrics]:
        values = list(results)

        return sorted(
            values,
            key=lambda result: (
                result.score,
                result.profit_factor,
                result.expectancy,
                result.total_return_pct,
                -result.max_drawdown_pct,
                result.total_trades,
            ),
            reverse=True,
        )

    def best(
        self,
        results: Iterable[BacktestMetrics],
    ) -> BacktestMetrics | None:
        ranked = self.rank(results)

        return ranked[0] if ranked else None
from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from jemba_core.lab.models import BacktestMetrics


class BacktestAnalyzer:
    """
    Analiza una secuencia de retornos por operación.

    Cada retorno debe expresarse en formato decimal:
    0.01 equivale a +1 %
    -0.02 equivale a -2 %
    """

    def __init__(self, initial_capital: float = 10_000.0) -> None:
        if initial_capital <= 0:
            raise ValueError("INITIAL_CAPITAL_MUST_BE_POSITIVE")

        self.initial_capital = float(initial_capital)

    def analyze(
        self,
        *,
        symbol: str,
        timeframe: str,
        trade_returns: Iterable[float],
    ) -> BacktestMetrics:
        clean_symbol = str(symbol).strip().upper()
        clean_timeframe = str(timeframe).strip()

        if not clean_symbol:
            raise ValueError("SYMBOL_IS_REQUIRED")

        if not clean_timeframe:
            raise ValueError("TIMEFRAME_IS_REQUIRED")

        returns = np.asarray(
            list(trade_returns),
            dtype=float,
        )

        if returns.ndim != 1:
            raise ValueError("TRADE_RETURNS_MUST_BE_ONE_DIMENSIONAL")

        if not np.isfinite(returns).all():
            raise ValueError("TRADE_RETURNS_MUST_BE_FINITE")

        if returns.size == 0:
            return self._empty_result(
                symbol=clean_symbol,
                timeframe=clean_timeframe,
            )

        equity = self._build_equity_curve(returns)

        wins_mask = returns > 0
        losses_mask = returns < 0
        breakeven_mask = returns == 0

        wins = int(wins_mask.sum())
        losses = int(losses_mask.sum())
        breakeven = int(breakeven_mask.sum())
        total_trades = int(returns.size)

        gross_profit = float(returns[wins_mask].sum()) if wins else 0.0
        gross_loss = abs(float(returns[losses_mask].sum())) if losses else 0.0

        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        elif gross_profit > 0:
            profit_factor = 999.0
        else:
            profit_factor = 0.0

        average_win = float(returns[wins_mask].mean()) if wins else 0.0
        average_loss = abs(float(returns[losses_mask].mean())) if losses else 0.0

        final_capital = float(equity[-1])
        net_profit = final_capital - self.initial_capital
        total_return_pct = (
            net_profit / self.initial_capital
        ) * 100.0

        max_drawdown_pct = self._max_drawdown_pct(equity)

        recovery_factor = (
            total_return_pct / max_drawdown_pct
            if max_drawdown_pct > 0
            else 0.0
        )

        expectancy = float(returns.mean())
        win_rate = wins / total_trades

        score = self._calculate_score(
            total_trades=total_trades,
            profit_factor=profit_factor,
            expectancy=expectancy,
            max_drawdown_pct=max_drawdown_pct,
            total_return_pct=total_return_pct,
        )

        return BacktestMetrics(
            symbol=clean_symbol,
            timeframe=clean_timeframe,
            initial_capital=round(self.initial_capital, 8),
            final_capital=round(final_capital, 8),
            net_profit=round(net_profit, 8),
            total_return_pct=round(total_return_pct, 8),
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            breakeven=breakeven,
            win_rate=round(win_rate, 8),
            gross_profit=round(gross_profit, 8),
            gross_loss=round(gross_loss, 8),
            profit_factor=round(profit_factor, 8),
            expectancy=round(expectancy, 8),
            average_win=round(average_win, 8),
            average_loss=round(average_loss, 8),
            best_trade=round(float(returns.max()), 8),
            worst_trade=round(float(returns.min()), 8),
            max_drawdown_pct=round(max_drawdown_pct, 8),
            recovery_factor=round(recovery_factor, 8),
            score=round(score, 8),
        )

    def _build_equity_curve(self, returns: np.ndarray) -> np.ndarray:
        growth = np.cumprod(1.0 + returns)

        return np.concatenate(
            (
                np.asarray([self.initial_capital], dtype=float),
                self.initial_capital * growth,
            )
        )

    @staticmethod
    def _max_drawdown_pct(equity: np.ndarray) -> float:
        peaks = np.maximum.accumulate(equity)

        drawdowns = np.divide(
            equity - peaks,
            peaks,
            out=np.zeros_like(equity, dtype=float),
            where=peaks != 0,
        )

        return abs(float(drawdowns.min())) * 100.0

    @staticmethod
    def _calculate_score(
        *,
        total_trades: int,
        profit_factor: float,
        expectancy: float,
        max_drawdown_pct: float,
        total_return_pct: float,
    ) -> float:
        sample_score = min(total_trades / 200.0, 1.0) * 15.0
        pf_score = min(max(profit_factor, 0.0) / 3.0, 1.0) * 30.0
        expectancy_score = min(max(expectancy + 0.02, 0.0) / 0.05, 1.0) * 20.0
        return_score = min(max(total_return_pct, 0.0) / 50.0, 1.0) * 20.0
        drawdown_score = max(1.0 - max_drawdown_pct / 30.0, 0.0) * 15.0

        return (
            sample_score
            + pf_score
            + expectancy_score
            + return_score
            + drawdown_score
        )

    def _empty_result(
        self,
        *,
        symbol: str,
        timeframe: str,
    ) -> BacktestMetrics:
        return BacktestMetrics(
            symbol=symbol,
            timeframe=timeframe,
            initial_capital=self.initial_capital,
            final_capital=self.initial_capital,
            net_profit=0.0,
            total_return_pct=0.0,
            total_trades=0,
            wins=0,
            losses=0,
            breakeven=0,
            win_rate=0.0,
            gross_profit=0.0,
            gross_loss=0.0,
            profit_factor=0.0,
            expectancy=0.0,
            average_win=0.0,
            average_loss=0.0,
            best_trade=0.0,
            worst_trade=0.0,
            max_drawdown_pct=0.0,
            recovery_factor=0.0,
            score=0.0,
        )
from jemba_core.backtest.equity_curve import EquityCurve
from jemba_core.backtest.metrics import Metrics


class Backtester:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance

    def run(self, trades):
        equity = EquityCurve.build(
            self.initial_balance,
            trades,
        )

        profit = equity[-1] - self.initial_balance

        return {
            "initial_balance": self.initial_balance,
            "final_balance": equity[-1],
            "profit": profit,
            "profit_percent": (profit / self.initial_balance) * 100,
            "win_rate": Metrics.win_rate(trades),
            "profit_factor": Metrics.profit_factor(trades),
            "average_win": Metrics.average_win(trades),
            "average_loss": Metrics.average_loss(trades),
            "expectancy": Metrics.expectancy(trades),
            "max_drawdown": Metrics.max_drawdown(equity),
            "sharpe_ratio": Metrics.sharpe_ratio(trades),
            "trades": len(trades),
            "equity": equity,
        }

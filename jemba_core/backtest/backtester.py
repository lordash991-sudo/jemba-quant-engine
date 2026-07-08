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

        return {
            "initial_balance": self.initial_balance,
            "final_balance": equity[-1],
            "profit": equity[-1] - self.initial_balance,
            "profit_percent": (
                (equity[-1] - self.initial_balance)
                / self.initial_balance
            )
            * 100,
            "win_rate": Metrics.win_rate(trades),
            "profit_factor": Metrics.profit_factor(trades),
            "trades": len(trades),
            "equity": equity,
        }

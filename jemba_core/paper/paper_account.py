class PaperAccount:

    def __init__(
        self,
        initial_balance: float = 10000.0,
        commission_rate: float = 0.0005,
    ):
        self.initial_balance = float(initial_balance)
        self.balance = float(initial_balance)
        self.equity = float(initial_balance)
        self.peak_equity = float(initial_balance)
        self.commission_rate = float(commission_rate)
        self.total_commissions = 0.0
        self.realized_pnl = 0.0
        self.trades = []

    def apply_trade_result(self, pnl: float, commission: float = 0.0):
        pnl = float(pnl)
        commission = float(commission)

        self.realized_pnl += pnl
        self.total_commissions += commission
        self.balance += pnl - commission
        self.equity = self.balance

        if self.equity > self.peak_equity:
            self.peak_equity = self.equity

        self.trades.append({
            "pnl": pnl,
            "commission": commission,
            "balance": self.balance,
            "equity": self.equity,
        })

        return self.balance

    def calculate_commission(self, notional: float):
        return float(notional) * self.commission_rate

    def drawdown(self):
        if self.peak_equity <= 0:
            return 0.0

        return (self.peak_equity - self.equity) / self.peak_equity

    def summary(self):
        return {
            "initial_balance": self.initial_balance,
            "balance": round(self.balance, 2),
            "equity": round(self.equity, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "total_commissions": round(self.total_commissions, 2),
            "drawdown": round(self.drawdown(), 4),
            "total_trades": len(self.trades),
        }

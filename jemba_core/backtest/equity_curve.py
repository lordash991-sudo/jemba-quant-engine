class EquityCurve:

    @staticmethod
    def build(initial_balance, trades):
        equity = [initial_balance]
        balance = initial_balance

        for trade in trades:
            balance += trade.pnl
            equity.append(balance)

        return equity

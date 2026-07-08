class PortfolioManager:
    def __init__(
        self,
        account_balance: float = 10000.0,
        risk_per_trade: float = 0.01,
        max_positions: int = 1,
    ):
        self.account_balance = float(account_balance)
        self.risk_per_trade = float(risk_per_trade)
        self.max_positions = int(max_positions)
        self.open_positions = []

    @property
    def risk_amount(self):
        return self.account_balance * self.risk_per_trade

    def can_open_position(self):
        return len(self.open_positions) < self.max_positions

    def calculate_position_size(self, entry: float, stop_loss: float):
        risk_per_unit = abs(float(entry) - float(stop_loss))

        if risk_per_unit <= 0:
            return 0.0

        return round(self.risk_amount / risk_per_unit, 6)

    def register_position(self, position: dict):
        if not self.can_open_position():
            return False

        self.open_positions.append(position)
        return True

    def close_position(self, pnl: float):
        if self.open_positions:
            self.open_positions.pop(0)

        self.account_balance += float(pnl)
        return self.account_balance

    def summary(self):
        return {
            "balance": round(self.account_balance, 2),
            "risk_per_trade": self.risk_per_trade,
            "risk_amount": round(self.risk_amount, 2),
            "open_positions": len(self.open_positions),
            "max_positions": self.max_positions,
        }

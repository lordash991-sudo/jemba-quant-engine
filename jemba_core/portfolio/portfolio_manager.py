class PortfolioManager:

    def __init__(
        self,
        account_balance: float,
        risk_per_trade: float = 0.01,
        max_positions: int = 1
    ):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.open_positions = []

    def can_open_position(self):
        return len(self.open_positions) < self.max_positions

    def risk_amount(self):
        return self.account_balance * self.risk_per_trade

    def calculate_position_size(self, entry_price: float, stop_loss: float):
        risk = abs(entry_price - stop_loss)

        if risk <= 0:
            return 0

        quantity = self.risk_amount() / risk
        return round(quantity, 6)

    def register_position(self, position):
        if self.can_open_position():
            self.open_positions.append(position)
            return True
        return False

    def close_position(self, pnl):
        self.account_balance += pnl

        if self.open_positions:
            self.open_positions.pop(0)

    def summary(self):
        return {
            "balance": round(self.account_balance, 2),
            "risk_per_trade": self.risk_per_trade,
            "risk_amount": round(self.risk_amount(), 2),
            "open_positions": len(self.open_positions),
            "max_positions": self.max_positions
        }

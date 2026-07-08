from dataclasses import dataclass


@dataclass
class RiskConfig:
    account_balance: float

    risk_percent: float = 1.0

    stop_loss_percent: float = 1.0

    take_profit_percent: float = 2.0

    leverage: int = 1


class RiskManager:
    def __init__(self, config: RiskConfig):

        self.config = config

    def capital_at_risk(self):

        return self.config.account_balance * self.config.risk_percent / 100

    def position_size(self, entry_price):

        risk = self.capital_at_risk()

        stop_distance = entry_price * self.config.stop_loss_percent / 100

        qty = risk / stop_distance

        return round(qty, 6)

    def stop_loss(self, entry):

        return round(
            entry * (1 - self.config.stop_loss_percent / 100),
            2,
        )

    def take_profit(self, entry):

        return round(
            entry * (1 + self.config.take_profit_percent / 100),
            2,
        )

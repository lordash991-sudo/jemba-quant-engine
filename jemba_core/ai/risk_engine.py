from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RiskResult:
    risk_amount: float
    position_size: float
    leverage: int
    stop_loss_pct: float
    take_profit_pct: float
    allowed: bool


class RiskEngine:
    def __init__(
        self,
        risk_per_trade: float = 0.01,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.04,
        max_leverage: int = 10,
    ):

        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_leverage = max_leverage

    def evaluate(
        self,
        capital: float,
    ) -> RiskResult:

        risk_amount = capital * self.risk_per_trade

        position_size = risk_amount / self.stop_loss_pct

        leverage = int(position_size / capital)

        leverage = max(1, leverage)

        leverage = min(leverage, self.max_leverage)

        return RiskResult(
            risk_amount=risk_amount,
            position_size=position_size,
            leverage=leverage,
            stop_loss_pct=self.stop_loss_pct,
            take_profit_pct=self.take_profit_pct,
            allowed=capital > 0,
        )

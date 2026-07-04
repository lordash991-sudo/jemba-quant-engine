from dataclasses import dataclass
from typing import Optional

from jemba_core.risk.risk_manager import RiskConfig, RiskManager
from jemba_core.strategy.strategy_engine import StrategyEngine


@dataclass
class TradeSignal:
    symbol: str
    timeframe: str
    action: str
    entry: float
    quantity: float
    stop_loss: float
    take_profit: float
    risk_amount: float


class SignalEngine:

    def __init__(self, account_balance: float = 1000):
        self.strategy = StrategyEngine()
        self.risk_config = RiskConfig(
            account_balance=account_balance,
            risk_percent=1,
            stop_loss_percent=1.5,
            take_profit_percent=3
        )
        self.risk = RiskManager(self.risk_config)

    def generate(self, df, symbol: str, timeframe: str) -> Optional[TradeSignal]:
        action = self.strategy.signal(df)

        if action == StrategyEngine.HOLD:
            return None

        entry = float(df.iloc[-1]['close'])

        quantity = self.risk.position_size(entry)
        stop_loss = self.risk.stop_loss(entry)
        take_profit = self.risk.take_profit(entry)
        risk_amount = self.risk.capital_at_risk()

        return TradeSignal(
            symbol=symbol,
            timeframe=timeframe,
            action=action,
            entry=entry,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=risk_amount
        )

from dataclasses import dataclass


@dataclass
class TradeSignal:
    symbol: str
    timeframe: str
    action: str
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float
    strategy: str = "JEMBA_AI_V1"


class SignalEngine:

    def generate_signal(
        self,
        symbol: str,
        timeframe: str,
        action: str,
        entry: float,
        confidence: float,
        atr: float = 0.0,
    ):
        if action not in ["BUY", "SELL"]:
            return None

        if atr <= 0:
            atr = entry * 0.01

        if action == "BUY":
            stop_loss = entry - atr
            take_profit = entry + (atr * 2)
        else:
            stop_loss = entry + atr
            take_profit = entry - (atr * 2)

        return TradeSignal(
            symbol=symbol,
            timeframe=timeframe,
            action=action,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
        )

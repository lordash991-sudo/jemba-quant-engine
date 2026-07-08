import time

from jemba_core.engine.quant_orchestrator import QuantOrchestrator
from jemba_core.events.event_bus import EventBus
from jemba_core.events.prediction_event import PredictionEvent
from jemba_core.events.risk_event import RiskEvent
from jemba_core.events.trade_signal_event import TradeSignalEvent
from jemba_core.execution.trade_engine import TradeEngine
from jemba_core.portfolio.portfolio_manager import PortfolioManager
from jemba_core.risk.risk_engine import RiskEngine


class LiveEngine:
    def __init__(self):
        self.event_bus = EventBus()

        self.symbols = [
            "BTC-USDT",
            "ETH-USDT",
            "SOL-USDT",
            "DOGE-USDT",
            "LINK-USDT",
            "XRP-USDT",
            "SUI-USDT",
            "PEPE-USDT",
            "BNB-USDT",
            "LTC-USDT",
            "ADA-USDT",
            "AVAX-USDT",
            "AAVE-USDT",
        ]

        self.portfolio = PortfolioManager(
            account_balance=10000,
            risk_per_trade=0.01,
        )

        self.trade_engine = TradeEngine(self.portfolio)
        self.risk_engine = RiskEngine()

        self.quant = QuantOrchestrator(
            account_balance=10000,
            min_confidence=0.70,
        )

    def cycle(self):
        best = self.quant.best_opportunity(self.symbols)

        if best is None:
            print("No hay señales.")
            return None

        print()
        print("=" * 60)
        print("MEJOR ACTIVO")
        print(best)

        action = best.get("action", "HOLD")
        symbol = best.get("symbol", "UNKNOWN")
        timeframe = best.get("timeframe", "1h")
        confidence = float(best.get("confidence", 0.0))
        buy_probability = float(best.get("buy_probability", 0.0))
        sell_probability = float(best.get("sell_probability", 0.0))

        prediction_event = PredictionEvent(
            source="LiveEngine",
            symbol=symbol,
            timeframe=timeframe,
            action=action,
            confidence=confidence,
            probability=max(buy_probability, sell_probability),
            model="RandomForest",
            metadata={
                "buy_probability": buy_probability,
                "sell_probability": sell_probability,
                "raw": best,
            },
        )

        self.event_bus.publish(prediction_event)

        validation = self.risk_engine.validate(
            portfolio=self.portfolio,
            confidence=confidence,
            position_size=1,
            has_open_position=not self.trade_engine.can_open_trade(),
        )

        print()
        print("RIESGO")
        print(validation)

        risk_event = RiskEvent(
            source="LiveEngine",
            approved=bool(validation.get("approved", False)),
            reason=",".join(validation.get("reasons", [])),
            risk_percent=float(self.portfolio.risk_per_trade),
            drawdown=0.0,
            consecutive_losses=0,
            metadata=validation,
        )

        self.event_bus.publish(risk_event)

        if not validation.get("approved", False):
            print()
            print("OPERACION BLOQUEADA")
            return {
                "prediction": prediction_event,
                "risk": risk_event,
                "trade_signal": None,
            }

        if action not in ["BUY", "SELL"]:
            print()
            print("SIN OPERACION: accion HOLD")
            return {
                "prediction": prediction_event,
                "risk": risk_event,
                "trade_signal": None,
            }

        trade_signal = TradeSignalEvent(
            source="LiveEngine",
            symbol=symbol,
            timeframe=timeframe,
            side=action,
            entry=float(best.get("entry", best.get("price", best.get("close", 0.0)))),
            stop_loss=float(best.get("stop_loss", best.get("sl", 0.0))),
            take_profit=float(best.get("take_profit", best.get("tp", 0.0))),
            confidence=confidence,
            strategy="JEMBA_AI_V1",
            metadata=best,
        )

        self.event_bus.publish(trade_signal)

        print()
        print("TRADE SIGNAL PUBLICADO")
        print(vars(trade_signal))

        return {
            "prediction": prediction_event,
            "risk": risk_event,
            "trade_signal": trade_signal,
        }

    def run(self):
        while True:
            self.cycle()

            print()
            print("Esperando siguiente ciclo...")

            time.sleep(60)

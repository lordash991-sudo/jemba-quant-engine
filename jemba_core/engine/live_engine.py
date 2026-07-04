import time

from jemba_core.engine.quant_orchestrator import QuantOrchestrator
from jemba_core.execution.trade_engine import TradeEngine
from jemba_core.portfolio.portfolio_manager import PortfolioManager
from jemba_core.risk.risk_engine import RiskEngine


class LiveEngine:

    def __init__(self):

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
            "AAVE-USDT"
        ]

        self.portfolio = PortfolioManager(
            account_balance=10000,
            risk_per_trade=0.01
        )

        self.trade_engine = TradeEngine(
            self.portfolio
        )

        self.risk_engine = RiskEngine()

        self.quant = QuantOrchestrator(
            account_balance=10000,
            min_confidence=0.70
        )

    def cycle(self):

        best = self.quant.best_opportunity(self.symbols)

        if best is None:
            print("No hay señales.")
            return

        print()

        print("="*60)

        print("MEJOR ACTIVO")

        print(best)

        validation = self.risk_engine.validate(
            portfolio=self.portfolio,
            confidence=best["confidence"],
            position_size=1,
            has_open_position=not self.trade_engine.can_open_trade()
        )

        print()

        print("RIESGO")

        print(validation)

        if not validation["approved"]:

            print()

            print("OPERACION BLOQUEADA")

            return

        print()

        print("OPERACION APROBADA")

    def run(self):

        while True:

            self.cycle()

            print()

            print("Esperando siguiente ciclo...")

            time.sleep(60)

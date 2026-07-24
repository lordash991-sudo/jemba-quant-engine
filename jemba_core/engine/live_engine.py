from __future__ import annotations

import logging
import time
from typing import Any

from jemba_core.ai.confidence_engine import ConfidenceEngine
from jemba_core.ai.predictor_engine import PredictorEngine
from jemba_core.execution.trade_engine import TradeEngine
from jemba_core.features.feature_engine import FeatureEngine
from jemba_core.portfolio.portfolio_manager import PortfolioManager
from jemba_core.risk.risk_engine import RiskEngine
from jemba_core.signals.signal_engine import SignalEngine
from jemba_core.signals.signal_ranker import SignalRanker


logger = logging.getLogger(__name__)


class LiveEngine:
    def __init__(
        self,
        symbols: list[str] | None = None,
        timeframe: str = "1h",
        account_balance: float = 10000.0,
        risk_per_trade: float = 0.01,
        max_positions: int = 1,
        min_confidence: float = 0.70,
        interval_seconds: int = 60,
    ) -> None:
        self.symbols = symbols or [
            "BTC-USDT",
            "ETH-USDT",
            "SOL-USDT",
        ]

        self.timeframe = timeframe
        self.interval_seconds = int(interval_seconds)
        self.running = False

        self.feature_engine = FeatureEngine()
        self.predictor_engine = PredictorEngine()
        self.confidence_engine = ConfidenceEngine()
        self.signal_engine = SignalEngine()
        self.ranking_engine = SignalRanker()

        self.risk_engine = RiskEngine(
            max_risk_per_trade=risk_per_trade,
            min_confidence=min_confidence,
            max_open_positions=max_positions,
        )

        self.portfolio = PortfolioManager(
            account_balance=account_balance,
            risk_per_trade=risk_per_trade,
            max_positions=max_positions,
        )

        self.trade_engine = TradeEngine(
            feature_engine=self.feature_engine,
            predictor_engine=self.predictor_engine,
            confidence_engine=self.confidence_engine,
            signal_engine=self.signal_engine,
            ranking_engine=self.ranking_engine,
            risk_engine=self.risk_engine,
            portfolio_manager=self.portfolio,
        )

    def start(self) -> None:
        self.running = True

        logger.info("LiveEngine iniciado en modo seguro.")
        logger.info(
            "Símbolos: %s | Timeframe: %s",
            self.symbols,
            self.timeframe,
        )

        while self.running:
            self.run_cycle()
            time.sleep(self.interval_seconds)

    def stop(self) -> None:
        self.running = False
        logger.info("LiveEngine detenido.")

    def run_cycle(self) -> list[Any]:
        results: list[Any] = []

        for symbol in self.symbols:
            try:
                result = self.trade_engine.process(
                    symbol=symbol,
                    timeframe=self.timeframe,
                )

                if result is not None:
                    results.append(result)

            except RuntimeError as exc:
                if str(exc) == "PREDICTOR_ENGINE_NOT_CONFIGURED":
                    logger.warning(
                        "Predictor no configurado. "
                        "No se generan señales para %s.",
                        symbol,
                    )
                    continue

                raise

        return results

    def summary(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "symbols": list(self.symbols),
            "timeframe": self.timeframe,
            "interval_seconds": self.interval_seconds,
            "portfolio": self.portfolio.summary(),
            "predictor_configured": getattr(
                self.predictor_engine,
                "is_configured",
                False,
            ),
        }

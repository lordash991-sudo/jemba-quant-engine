from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradeDecision:
    symbol: str
    side: str
    confidence: float
    size: float
    probability: float


class TradeEngine:
    def __init__(
        self,
        feature_engine,
        predictor_engine,
        confidence_engine,
        signal_engine,
        ranking_engine,
        risk_engine,
        portfolio_manager,
    ):
        self.feature_engine = feature_engine
        self.predictor_engine = predictor_engine
        self.confidence_engine = confidence_engine
        self.signal_engine = signal_engine
        self.ranking_engine = ranking_engine
        self.risk_engine = risk_engine
        self.portfolio_manager = portfolio_manager

    def execute(self, candles, symbol="BTCUSDT"):

        features = self.feature_engine.latest(candles)

        prediction = self.predictor_engine.latest(features)

        confidence = self.confidence_engine.calculate(prediction)

        signal = self.signal_engine.generate(prediction, confidence)

        ranking = self.ranking_engine.rank(signal)

        risk = self.risk_engine.evaluate(ranking)

        position = self.portfolio_manager.allocate(risk)

        return TradeDecision(
            symbol=symbol,
            side=signal,
            confidence=confidence,
            size=position,
            probability=prediction["probability_long"],
        )

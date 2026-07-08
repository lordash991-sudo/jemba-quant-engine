from jemba_core.engine.trading_opportunity import TradingOpportunity


class PipelineEngine:
    def __init__(
        self,
        feature_engine,
        predictor,
        confidence_engine,
        signal_engine,
        ranking_engine,
        risk_engine,
        portfolio_manager,
        min_confidence: float = 0.70,
    ):
        self.feature_engine = feature_engine
        self.predictor = predictor
        self.confidence_engine = confidence_engine
        self.signal_engine = signal_engine
        self.ranking_engine = ranking_engine
        self.risk_engine = risk_engine
        self.portfolio_manager = portfolio_manager
        self.min_confidence = float(min_confidence)

    def process(self, symbol, timeframe, candles):
        try:
            features = self.feature_engine.generate(candles)

            if features is None:
                return None

            prediction = self.predictor.predict(
                symbol=symbol,
                timeframe=timeframe,
                features=features,
            )

            if prediction is None:
                return None

            ai_probability = float(getattr(prediction, "probability", 0.0))
            action = getattr(prediction, "action", "HOLD")

            last_row = features.iloc[-1]

            trend_score = self._trend_score(last_row)
            volatility_score = self._volatility_score(last_row)
            momentum_score = self._momentum_score(last_row)

            confidence_breakdown = self.confidence_engine.calculate(
                ai_probability=ai_probability,
                trend_score=trend_score,
                volatility_score=volatility_score,
                momentum_score=momentum_score,
            )

            confidence = float(confidence_breakdown.score)

            if confidence < self.min_confidence:
                return None

            entry = float(last_row["close"])
            atr = float(last_row.get("ATR", entry * 0.01))

            signal = self.signal_engine.generate_signal(
                symbol=symbol,
                timeframe=timeframe,
                action=action,
                entry=entry,
                confidence=confidence,
                atr=atr,
            )

            if signal is None:
                return None

            ranked = self.ranking_engine.rank([signal])

            if not ranked:
                return None

            signal = ranked[0]

            position_size = self.portfolio_manager.calculate_position_size(
                entry=signal.entry,
                stop_loss=signal.stop_loss,
            )

            risk = self.risk_engine.validate(
                portfolio=self.portfolio_manager,
                confidence=signal.confidence,
                position_size=position_size,
                has_open_position=not self.portfolio_manager.can_open_position(),
            )

            if not risk.get("approved", False):
                return None

            opportunity = TradingOpportunity(
                symbol=signal.symbol,
                timeframe=signal.timeframe,
                action=signal.action,
                entry=signal.entry,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                confidence=signal.confidence,
                ai_probability=ai_probability,
                position_size=position_size,
                approved=True,
                reason="APPROVED",
                metadata={
                    "prediction": prediction,
                    "confidence_breakdown": confidence_breakdown,
                    "risk": risk,
                },
            )

            return opportunity

        except Exception:
            return None

    def _trend_score(self, row):
        if "EMA20" in row and "EMA50" in row and row["EMA20"] > row["EMA50"]:
            return 1.0

        return 0.5

    def _volatility_score(self, row):
        atr_pct = float(row.get("ATR_PCT", 0.01))

        if atr_pct <= 0:
            return 0.5

        if atr_pct <= 0.03:
            return 1.0

        if atr_pct <= 0.06:
            return 0.7

        return 0.4

    def _momentum_score(self, row):
        rsi = float(row.get("RSI", 50))

        if 45 <= rsi <= 70:
            return 1.0

        if 35 <= rsi < 45 or 70 < rsi <= 80:
            return 0.7

        return 0.4

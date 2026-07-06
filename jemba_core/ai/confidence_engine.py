from dataclasses import dataclass


@dataclass
class ConfidenceBreakdown:
    ai: float
    trend: float
    volatility: float
    momentum: float

    @property
    def score(self):
        return round(
            self.ai * 0.40
            + self.trend * 0.25
            + self.volatility * 0.15
            + self.momentum * 0.20,
            4,
        )


class ConfidenceEngine:

    def calculate(
        self,
        ai_probability: float,
        trend_score: float,
        volatility_score: float,
        momentum_score: float,
    ):

        breakdown = ConfidenceBreakdown(
            ai=max(0, min(ai_probability, 1)),
            trend=max(0, min(trend_score, 1)),
            volatility=max(0, min(volatility_score, 1)),
            momentum=max(0, min(momentum_score, 1)),
        )

        return breakdown
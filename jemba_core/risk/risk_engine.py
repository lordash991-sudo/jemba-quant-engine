class RiskEngine:

    def __init__(
        self,
        max_daily_drawdown=0.05,
        max_consecutive_losses=3,
        min_confidence=0.70,
        max_risk_per_trade=0.01
    ):

        self.max_daily_drawdown = max_daily_drawdown
        self.max_consecutive_losses = max_consecutive_losses
        self.min_confidence = min_confidence
        self.max_risk_per_trade = max_risk_per_trade

    def validate(
        self,
        portfolio,
        confidence,
        consecutive_losses=0,
        daily_drawdown=0,
        position_size=0,
        has_open_position=False
    ):

        reasons = []

        if confidence < self.min_confidence:
            reasons.append("LOW_CONFIDENCE")

        if consecutive_losses >= self.max_consecutive_losses:
            reasons.append("MAX_CONSECUTIVE_LOSSES")

        if daily_drawdown >= self.max_daily_drawdown:
            reasons.append("MAX_DAILY_DRAWDOWN")

        if has_open_position:
            reasons.append("POSITION_ALREADY_OPEN")

        if position_size <= 0:
            reasons.append("INVALID_POSITION_SIZE")

        approved = len(reasons) == 0

        return {
            "approved": approved,
            "reasons": reasons
        }

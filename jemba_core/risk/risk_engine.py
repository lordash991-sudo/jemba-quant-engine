class RiskEngine:

    def __init__(
        self,
        min_confidence: float = 0.70,
        max_daily_drawdown: float = 0.05,
        max_consecutive_losses: int = 3,
    ):
        self.min_confidence = float(min_confidence)
        self.max_daily_drawdown = float(max_daily_drawdown)
        self.max_consecutive_losses = int(max_consecutive_losses)

    def validate(
        self,
        portfolio,
        confidence: float,
        position_size: float,
        has_open_position: bool = False,
        consecutive_losses: int = 0,
        daily_drawdown: float = 0.0,
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

        return {
            "approved": len(reasons) == 0,
            "reasons": reasons,
        }

from jemba_core.risk.models import RiskDecision, RiskRequest
from jemba_core.risk.position_sizer import PositionSizer


class RiskEngine:
    def __init__(
        self,
        max_risk_per_trade: float = 0.02,
        min_confidence: float = 0.75,
        max_open_positions: int = 5,
    ):
        self.max_risk_per_trade = max_risk_per_trade
        self.min_confidence = min_confidence
        self.max_open_positions = max_open_positions
        self.position_sizer = PositionSizer()

    def evaluate(self, request: RiskRequest) -> RiskDecision:
        if request.account_balance <= 0:
            return RiskDecision(False, "NO_BALANCE")

        if request.confidence < self.min_confidence:
            return RiskDecision(False, "LOW_CONFIDENCE")

        if request.open_positions >= self.max_open_positions:
            return RiskDecision(False, "MAX_OPEN_POSITIONS")

        position_size = self.position_sizer.calculate(
            request,
            self.max_risk_per_trade,
        )

        max_loss = request.account_balance * self.max_risk_per_trade

        return RiskDecision(
            approved=True,
            reason="APPROVED",
            risk_percent=self.max_risk_per_trade,
            position_size=position_size,
            max_loss=max_loss,
        )

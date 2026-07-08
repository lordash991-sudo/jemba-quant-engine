from jemba_core.risk.models import RiskRequest


class PositionSizer:
    def calculate(self, request: RiskRequest, risk_percent: float) -> float:
        stop_distance = abs(request.entry_price - request.stop_loss_price)

        if stop_distance <= 0:
            raise ValueError("stop_loss_price must be different from entry_price")

        max_loss = request.account_balance * risk_percent
        return max_loss / stop_distance

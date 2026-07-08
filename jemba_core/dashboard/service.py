from jemba_core.dashboard.models import DashboardSnapshot


class DashboardService:
    def build_snapshot(
        self,
        balance: float,
        equity: float,
        pnl_today: float,
        drawdown: float,
        open_positions: int,
        current_regime: str = "UNKNOWN",
        regime_confidence: float = 0.0,
        ai_confidence: float = 0.0,
        risk_of_ruin: float = 0.0,
        system_status: str = "RUNNING",
    ) -> DashboardSnapshot:
        return DashboardSnapshot(
            balance=balance,
            equity=equity,
            pnl_today=pnl_today,
            drawdown=drawdown,
            open_positions=open_positions,
            current_regime=current_regime,
            regime_confidence=regime_confidence,
            ai_confidence=ai_confidence,
            risk_of_ruin=risk_of_ruin,
            system_status=system_status,
        )

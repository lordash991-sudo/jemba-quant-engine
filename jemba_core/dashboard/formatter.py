from jemba_core.dashboard.models import DashboardSnapshot


class DashboardFormatter:
    def format_snapshot(self, snapshot: DashboardSnapshot) -> dict:
        return {
            "balance": round(snapshot.balance, 2),
            "equity": round(snapshot.equity, 2),
            "pnl_today": round(snapshot.pnl_today, 2),
            "drawdown_percent": round(snapshot.drawdown * 100, 2),
            "open_positions": snapshot.open_positions,
            "current_regime": snapshot.current_regime,
            "regime_confidence_percent": round(
                snapshot.regime_confidence * 100,
                2,
            ),
            "ai_confidence_percent": round(snapshot.ai_confidence * 100, 2),
            "risk_of_ruin_percent": round(snapshot.risk_of_ruin * 100, 2),
            "system_status": snapshot.system_status,
        }

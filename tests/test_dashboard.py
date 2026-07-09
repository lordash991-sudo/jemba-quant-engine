from jemba_core.dashboard.formatter import DashboardFormatter
from jemba_core.dashboard.service import DashboardService


def test_dashboard_snapshot():

    service = DashboardService()

    snapshot = service.build_snapshot(
        balance=10000,
        equity=10450,
        pnl_today=450,
        drawdown=0.025,
        open_positions=3,
        current_regime="TREND",
        regime_confidence=0.91,
        ai_confidence=0.87,
        risk_of_ruin=0.01,
    )

    assert snapshot.balance == 10000
    assert snapshot.equity == 10450
    assert snapshot.current_regime == "TREND"


def test_dashboard_formatter():

    service = DashboardService()
    formatter = DashboardFormatter()

    snapshot = service.build_snapshot(
        balance=10000,
        equity=10450,
        pnl_today=450,
        drawdown=0.025,
        open_positions=3,
        current_regime="TREND",
        regime_confidence=0.91,
        ai_confidence=0.87,
        risk_of_ruin=0.01,
    )

    data = formatter.format_snapshot(snapshot)

    assert data["balance"] == 10000
    assert data["drawdown_percent"] == 2.5
    assert data["regime_confidence_percent"] == 91
    assert data["system_status"] == "RUNNING"

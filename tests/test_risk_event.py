from jemba_core.events.risk_event import RiskEvent


def test_risk_event():
    event = RiskEvent(
        source="RiskEngine",
        approved=False,
        reason="LOW_CONFIDENCE",
        risk_percent=0.01,
        drawdown=0.03,
        consecutive_losses=2,
    )

    assert event.event_type == "RiskEvent"
    assert event.source == "RiskEngine"
    assert event.approved is False
    assert event.reason == "LOW_CONFIDENCE"
    assert event.risk_percent == 0.01
    assert event.drawdown == 0.03
    assert event.consecutive_losses == 2

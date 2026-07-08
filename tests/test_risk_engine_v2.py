from jemba_core.risk.models import RiskRequest
from jemba_core.risk.risk_engine import RiskEngine


def test_risk_engine_approves_valid_trade():
    engine = RiskEngine()
    request = RiskRequest(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=100,
        stop_loss_price=98,
        confidence=0.90,
        account_balance=10000,
    )

    decision = engine.evaluate(request)

    assert decision.approved is True
    assert decision.reason == "APPROVED"
    assert decision.max_loss == 200
    assert decision.position_size == 100


def test_risk_engine_rejects_low_confidence():
    engine = RiskEngine(min_confidence=0.80)
    request = RiskRequest(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=100,
        stop_loss_price=98,
        confidence=0.70,
        account_balance=10000,
    )

    decision = engine.evaluate(request)

    assert decision.approved is False
    assert decision.reason == "LOW_CONFIDENCE"


def test_risk_engine_rejects_no_balance():
    engine = RiskEngine()
    request = RiskRequest(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=100,
        stop_loss_price=98,
        confidence=0.90,
        account_balance=0,
    )

    decision = engine.evaluate(request)

    assert decision.approved is False
    assert decision.reason == "NO_BALANCE"


def test_risk_engine_rejects_max_open_positions():
    engine = RiskEngine(max_open_positions=2)
    request = RiskRequest(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=100,
        stop_loss_price=98,
        confidence=0.90,
        account_balance=10000,
        open_positions=2,
    )

    decision = engine.evaluate(request)

    assert decision.approved is False
    assert decision.reason == "MAX_OPEN_POSITIONS"

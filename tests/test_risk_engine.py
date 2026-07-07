from jemba_core.ai.risk_engine import RiskEngine


def test_risk_amount():

    engine = RiskEngine()

    result = engine.evaluate(10000)

    assert result.risk_amount == 100


def test_position():

    engine = RiskEngine()

    result = engine.evaluate(10000)

    assert result.position_size == 5000


def test_leverage():

    engine = RiskEngine()

    result = engine.evaluate(10000)

    assert result.leverage == 1


def test_allowed():

    engine = RiskEngine()

    result = engine.evaluate(10000)

    assert result.allowed


def test_stop_loss():

    engine = RiskEngine()

    result = engine.evaluate(10000)

    assert result.stop_loss_pct == 0.02


def test_take_profit():

    engine = RiskEngine()

    result = engine.evaluate(10000)

    assert result.take_profit_pct == 0.04

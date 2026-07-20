from jemba_core.execution import (
    ExecutionBridge,
    ExecutionRequest,
    FillSimulator,
    OrderSide,
    OrderType,
    SlippageModel,
)


def valid_request(**overrides):
    values = {
        "symbol": "BTCUSDT",
        "side": OrderSide.BUY,
        "order_type": OrderType.MARKET,
        "entry_price": 100.0,
        "quantity": 2.0,
        "leverage": 10,
        "risk_percent": 1.0,
        "stop_loss": 95.0,
        "take_profit": 110.0,
        "available_margin": 100.0,
    }

    values.update(overrides)
    return ExecutionRequest(**values)


def test_bridge_executes_valid_request():
    bridge = ExecutionBridge(
        fill_simulator=FillSimulator(slippage_model=SlippageModel(seed=1))
    )

    result = bridge.execute(valid_request())

    assert result.approved is True
    assert result.order_id is not None
    assert result.executed_price > 0.0


def test_bridge_rejects_decision():
    result = ExecutionBridge().execute(valid_request(decision_approved=False))

    assert result.approved is False
    assert result.reason == "DECISION_REJECTED"
    assert result.order_id is None


def test_bridge_rejects_duplicate_position():
    result = ExecutionBridge().execute(valid_request(duplicate_position=True))

    assert result.approved is False
    assert result.reason == "DUPLICATE_POSITION"


def test_bridge_rejects_closed_market():
    result = ExecutionBridge().execute(valid_request(market_open=False))

    assert result.approved is False
    assert result.reason == "MARKET_CLOSED"


def test_bridge_rejects_portfolio_failure():
    result = ExecutionBridge().execute(valid_request(portfolio_approved=False))

    assert result.approved is False
    assert result.reason == "PORTFOLIO_REJECTED"

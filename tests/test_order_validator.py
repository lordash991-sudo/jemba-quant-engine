from jemba_core.execution import (
    ExecutionRequest,
    OrderSide,
    OrderType,
    OrderValidator,
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


def test_valid_order():
    result = OrderValidator().validate(valid_request())

    assert result.approved is True
    assert result.reasons == ()


def test_rejects_invalid_quantity():
    result = OrderValidator().validate(valid_request(quantity=0.0))

    assert result.approved is False
    assert "INVALID_QUANTITY" in result.reasons


def test_rejects_invalid_buy_stop():
    result = OrderValidator().validate(valid_request(stop_loss=105.0))

    assert "INVALID_STOP_LOSS" in result.reasons


def test_rejects_low_risk_reward():
    result = OrderValidator().validate(
        valid_request(
            stop_loss=90.0,
            take_profit=105.0,
        )
    )

    assert "RISK_REWARD_TOO_LOW" in result.reasons


def test_rejects_insufficient_margin():
    result = OrderValidator().validate(
        valid_request(
            quantity=100.0,
            available_margin=10.0,
        )
    )

    assert "INSUFFICIENT_MARGIN" in result.reasons


def test_rejects_kill_switch():
    result = OrderValidator().validate(valid_request(kill_switch=True))

    assert result.primary_reason == "KILL_SWITCH_ACTIVE"

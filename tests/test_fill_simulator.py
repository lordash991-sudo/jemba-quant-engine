from datetime import datetime

from jemba_core.execution import (
    CommissionModel,
    ExecutionRequest,
    FillSimulator,
    OrderSide,
    OrderType,
    SlippageModel,
)


def test_fill_simulator_generates_fill():
    request = ExecutionRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        entry_price=100.0,
        quantity=2.0,
        leverage=10,
        risk_percent=1.0,
        stop_loss=95.0,
        take_profit=110.0,
        available_margin=100.0,
    )

    simulator = FillSimulator(
        slippage_model=SlippageModel(seed=4),
        commission_model=CommissionModel(),
    )

    result = simulator.execute(request)

    assert result.approved is True
    assert result.executed_price > 100.0
    assert result.quantity == 2.0
    assert result.margin_used > 0.0
    assert result.commission > 0.0
    assert result.order_id is not None
    assert isinstance(result.timestamp, datetime)

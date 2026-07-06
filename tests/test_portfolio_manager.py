from jemba_core.portfolio.portfolio_manager import PortfolioManager


def test_calculate_position_size():
    portfolio = PortfolioManager(
        account_balance=10000,
        risk_per_trade=0.01,
    )

    size = portfolio.calculate_position_size(
        entry=100,
        stop_loss=95,
    )

    assert size == 20


def test_register_and_close_position():
    portfolio = PortfolioManager(
        account_balance=10000,
        risk_per_trade=0.01,
        max_positions=1,
    )

    assert portfolio.can_open_position() is True

    opened = portfolio.register_position({
        "symbol": "BTC-USDT",
        "side": "BUY",
    })

    assert opened is True
    assert portfolio.can_open_position() is False

    portfolio.close_position(100)

    summary = portfolio.summary()

    assert summary["balance"] == 10100
    assert summary["open_positions"] == 0

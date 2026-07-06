from jemba_core.paper.paper_account import PaperAccount


def test_paper_account_apply_trade_result():
    account = PaperAccount(initial_balance=10000, commission_rate=0.001)

    commission = account.calculate_commission(1000)
    account.apply_trade_result(pnl=100, commission=commission)

    summary = account.summary()

    assert summary["balance"] == 10099.0
    assert summary["equity"] == 10099.0
    assert summary["realized_pnl"] == 100.0
    assert summary["total_commissions"] == 1.0
    assert summary["total_trades"] == 1


def test_paper_account_drawdown():
    account = PaperAccount(initial_balance=10000)

    account.apply_trade_result(pnl=500)
    account.apply_trade_result(pnl=-250)

    assert account.drawdown() > 0

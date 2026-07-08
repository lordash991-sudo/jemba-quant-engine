from jemba_core.paper.paper_account import PaperAccount


def test_initial_state():
    account = PaperAccount(10000)

    state = account.state()

    assert state.balance == 10000
    assert state.equity == 10000
    assert state.used_margin == 0


def test_reserve_margin():
    account = PaperAccount(10000)

    result = account.reserve_margin(1000)

    assert result is True
    assert account.used_margin == 1000
    assert account.free_margin == 9000


def test_cannot_reserve_more_than_free_margin():
    account = PaperAccount(10000)

    result = account.reserve_margin(11000)

    assert result is False
    assert account.used_margin == 0


def test_release_margin():
    account = PaperAccount(10000)

    account.reserve_margin(1000)
    account.release_margin(400)

    assert account.used_margin == 600


def test_apply_realized_pnl():
    account = PaperAccount(10000)

    account.apply_realized_pnl(250)

    assert account.balance == 10250
    assert account.realized_pnl == 250


def test_update_unrealized_pnl():
    account = PaperAccount(10000)

    account.update_unrealized_pnl(120)

    assert account.equity == 10120
    assert account.unrealized_pnl == 120

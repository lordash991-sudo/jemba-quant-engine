from jemba_core.paper.paper_account import PaperAccount
from jemba_core.paper.paper_broker import PaperBroker


def test_place_order():
    broker = PaperBroker(PaperAccount(10000))

    order = broker.place_order(
        symbol="BTCUSDT",
        side="LONG",
        size=1000,
        price=65000,
    )

    assert order.status == "FILLED"
    assert broker.get_position("BTCUSDT") is not None


def test_reject_invalid_size():
    broker = PaperBroker(PaperAccount(10000))

    order = broker.place_order(
        symbol="BTCUSDT",
        side="LONG",
        size=0,
        price=65000,
    )

    assert order.status == "REJECTED"


def test_reject_not_enough_margin():
    broker = PaperBroker(PaperAccount(1000))

    order = broker.place_order(
        symbol="BTCUSDT",
        side="LONG",
        size=2000,
        price=65000,
    )

    assert order.status == "REJECTED"


def test_close_position():
    broker = PaperBroker(PaperAccount(10000))

    broker.place_order(
        symbol="BTCUSDT",
        side="LONG",
        size=1000,
        price=65000,
    )

    position = broker.close_position("BTCUSDT")

    assert position.symbol == "BTCUSDT"
    assert broker.get_position("BTCUSDT") is None


def test_balance_and_equity():
    broker = PaperBroker(PaperAccount(10000))

    assert broker.balance() == 10000
    assert broker.equity() == 10000

from datetime import datetime

from jemba_core.paper.paper_position import PaperPosition


def test_close_buy():

    p = PaperPosition(

        symbol="BTC-USDT",

        side="BUY",

        entry=100,

        stop_loss=95,

        take_profit=110,

        quantity=2,

        confidence=0.90,

        opened_at=datetime.utcnow()

    )

    pnl = p.close(

        exit_price=110,

        commission=1

    )

    assert p.status == "CLOSED"

    assert pnl == 19


def test_close_sell():

    p = PaperPosition(

        symbol="BTC-USDT",

        side="SELL",

        entry=100,

        stop_loss=105,

        take_profit=90,

        quantity=2,

        confidence=0.90,

        opened_at=datetime.utcnow()

    )

    pnl = p.close(

        exit_price=90,

        commission=1

    )

    assert pnl == 19

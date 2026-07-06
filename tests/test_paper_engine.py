from datetime import datetime

from jemba_core.paper.paper_engine import PaperEngine
from jemba_core.paper.paper_position import PaperPosition


def test_open_close_position():

    engine = PaperEngine()

    position = PaperPosition(

        symbol="BTC-USDT",

        side="BUY",

        entry=100,

        stop_loss=95,

        take_profit=110,

        quantity=2,

        confidence=0.90,

        opened_at=datetime.utcnow()

    )

    engine.open_position(position)

    assert engine.has_open_position("BTC-USDT")

    pnl = engine.close_position(

        position,

        110

    )

    assert pnl > 0

    summary = engine.summary()

    assert summary["closed_positions"] == 1

    assert summary["account"]["balance"] > 10000

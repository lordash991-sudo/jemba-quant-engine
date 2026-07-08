from jemba_core.backtest.backtester import Backtester
from jemba_core.backtest.trade import Trade


def test_backtester():

    trades = [
        Trade("BTC","LONG",100,105,1,100,5),
        Trade("BTC","LONG",105,103,1,-50,-2),
        Trade("BTC","SHORT",103,99,1,120,4),
    ]

    report = Backtester().run(trades)

    assert report["trades"] == 3
    assert report["final_balance"] == 10170
    assert report["profit"] == 170

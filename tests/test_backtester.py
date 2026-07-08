from jemba_core.backtest.backtester import Backtester
from jemba_core.backtest.metrics import Metrics
from jemba_core.backtest.trade import Trade


def sample_trades():
    return [
        Trade("BTC", "LONG", 100, 105, 1, 100, 5),
        Trade("BTC", "LONG", 105, 103, 1, -50, -2),
        Trade("BTC", "SHORT", 103, 99, 1, 120, 4),
    ]


def test_backtester():
    report = Backtester().run(sample_trades())

    assert report["trades"] == 3
    assert report["final_balance"] == 10170
    assert report["profit"] == 170
    assert report["average_win"] == 110
    assert report["average_loss"] == -50
    assert report["expectancy"] == 56.66666666666666
    assert report["sortino_ratio"] > 0
    assert report["calmar_ratio"] > 0
    assert report["recovery_factor"] > 0


def test_max_drawdown():
    equity = [10000, 10100, 10050, 10220]

    assert Metrics.max_drawdown(equity) == 50 / 10100


def test_profit_factor():
    assert Metrics.profit_factor(sample_trades()) == 220 / 50


def test_sharpe_ratio_is_calculated():
    assert Metrics.sharpe_ratio(sample_trades()) > 0


def test_sortino_ratio_is_calculated():
    assert Metrics.sortino_ratio(sample_trades()) > 0


def test_calmar_ratio_is_calculated():
    equity = [10000, 10100, 10050, 10220]

    assert Metrics.calmar_ratio(equity, sample_trades()) > 0


def test_recovery_factor_is_calculated():
    equity = [10000, 10100, 10050, 10220]

    assert Metrics.recovery_factor(equity) > 0

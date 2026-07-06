from jemba_core.paper.paper_statistics import PaperStatistics


def test_paper_statistics():
    trades = [
        {"pnl": 100},
        {"pnl": -50},
        {"pnl": 200},
    ]

    stats = PaperStatistics.calculate(trades)

    assert stats["total_trades"] == 3
    assert stats["wins"] == 2
    assert stats["losses"] == 1
    assert stats["win_rate"] == 0.6667
    assert stats["gross_profit"] == 300
    assert stats["gross_loss"] == 50
    assert stats["profit_factor"] == 6.0
    assert stats["expectancy"] == 83.3333


def test_paper_statistics_empty():
    stats = PaperStatistics.calculate([])

    assert stats["total_trades"] == 0
    assert stats["win_rate"] == 0.0

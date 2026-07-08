from jemba_core.signals.signal_ranker import RankedSignal, SignalRanker


def test_rank_order():

    ranker = SignalRanker()

    signals = [
        RankedSignal("BTC", 0.82),
        RankedSignal("ETH", 0.71),
        RankedSignal("DOGE", 0.95),
        RankedSignal("SOL", 0.88),
    ]

    ranked = ranker.rank(signals)

    assert ranked[0].symbol == "DOGE"
    assert ranked[1].symbol == "SOL"
    assert ranked[2].symbol == "BTC"
    assert ranked[3].symbol == "ETH"


def test_best_signal():

    ranker = SignalRanker()

    signals = [
        RankedSignal("BTC", 0.81),
        RankedSignal("ETH", 0.92),
        RankedSignal("XRP", 0.76),
    ]

    best = ranker.best(signals)

    assert best.symbol == "ETH"
    assert best.confidence == 0.92


def test_empty():

    ranker = SignalRanker()

    assert ranker.best([]) is None


def test_ignore_none():

    ranker = SignalRanker()

    signals = [None, RankedSignal("BTC", 0.60), None, RankedSignal("SOL", 0.80)]

    ranked = ranker.rank(signals)

    assert len(ranked) == 2
    assert ranked[0].symbol == "SOL"

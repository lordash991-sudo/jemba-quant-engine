from jemba_core.ai.signal_engine import SignalResult
from jemba_core.ai.ranking_engine import RankingEngine


def signal(action, confidence):

    return SignalResult(
        action=action,
        confidence=confidence,
        prediction=1,
        probability=0.9,
    )


def test_ranking():

    engine = RankingEngine()

    ranked = engine.rank(

        [

            ("BTC", signal("BUY",95),1.0),

            ("ETH", signal("BUY",80),1.0),

            ("SOL", signal("SELL",70),1.0),

        ]

    )

    assert ranked[0].symbol=="BTC"

    assert ranked[1].symbol=="ETH"

    assert ranked[2].symbol=="SOL"


def test_best():

    engine=RankingEngine()

    best=engine.best(

        [

            ("BTC",signal("BUY",93),1),

            ("ETH",signal("BUY",82),1),

        ]

    )

    assert best.symbol=="BTC"


def test_hold_removed():

    engine=RankingEngine()

    ranked=engine.rank(

        [

            ("BTC",signal("HOLD",95),1),

            ("ETH",signal("BUY",80),1),

        ]

    )

    assert len(ranked)==1

    assert ranked[0].symbol=="ETH"


def test_empty():

    engine=RankingEngine()

    ranked=engine.rank([])

    assert ranked==[]

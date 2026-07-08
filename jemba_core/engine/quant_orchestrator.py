from jemba_core.signals.signal_ranker import SignalRanker


class QuantOrchestrator:
    def __init__(self, account_balance=10000, min_confidence=0.70):

        self.account_balance = account_balance
        self.min_confidence = min_confidence

        self.ranking_engine = SignalRanker()

    def scan(self, symbols, timeframe="1h"):
        """
        Aquí posteriormente se conectará SignalEngine.
        Por ahora devolvemos una lista vacía.
        """

        return []

    def best_opportunity(self, symbols, timeframe="1h"):

        signals = self.scan(symbols, timeframe)

        if not signals:
            return None

        ranked = self.ranking_engine.rank(signals)

        if not ranked:
            return None

        return ranked[0]

from dataclasses import dataclass


@dataclass
class RankedSignal:
    symbol: str
    confidence: float
    signal: object = None


class SignalRanker:
    def rank(self, signals):

        valid = [s for s in signals if s is not None]

        valid.sort(key=lambda x: x.confidence, reverse=True)

        return valid

    def best(self, signals):

        ranked = self.rank(signals)

        if not ranked:
            return None

        return ranked[0]

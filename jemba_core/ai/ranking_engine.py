from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from jemba_core.ai.signal_engine import SignalResult


@dataclass(slots=True)
class RankedSignal:
    symbol: str
    score: float
    signal: SignalResult


class RankingEngine:

    def score(self, signal: SignalResult, volatility: float = 1.0) -> float:

        base = signal.confidence

        if signal.action == "BUY":
            base += 5

        elif signal.action == "SELL":
            base += 5

        return base * volatility

    def rank(self, signals: Iterable[tuple[str, SignalResult, float]]):

        ranked = []

        for symbol, signal, volatility in signals:

            if signal.action == "HOLD":
                continue

            ranked.append(
                RankedSignal(
                    symbol=symbol,
                    score=self.score(signal, volatility),
                    signal=signal,
                )
            )

        ranked.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return ranked

    def best(self, signals):

        ranked = self.rank(signals)

        if not ranked:
            return None

        return ranked[0]

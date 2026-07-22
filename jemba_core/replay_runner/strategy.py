from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict, deque

from jemba_core.paper_broker import PositionSide
from jemba_core.replay_runner.models import (
    ReplayStrategyContext,
    ReplayTradeSignal,
)


class ReplayStrategy(ABC):
    """Strategy interface consumed by ReplayStrategyRunner."""

    @abstractmethod
    def on_candle(
        self,
        context: ReplayStrategyContext,
    ) -> ReplayTradeSignal | None:
        """Return a trade signal or None to hold."""


class MovingAverageCrossStrategy(ReplayStrategy):
    """
    Small deterministic reference strategy.

    It exists to validate the replay pipeline. It is not presented
    as a profitable production strategy, despite humanity's touching
    tendency to trust anything containing two moving averages.
    """

    def __init__(
        self,
        *,
        fast_period: int = 3,
        slow_period: int = 5,
        quantity: float = 1.0,
        leverage: int = 10,
        stop_loss_percent: float = 0.02,
        take_profit_percent: float = 0.04,
        confidence: float = 75.0,
    ) -> None:
        if not isinstance(fast_period, int):
            raise TypeError("FAST_PERIOD_MUST_BE_INTEGER")

        if not isinstance(slow_period, int):
            raise TypeError("SLOW_PERIOD_MUST_BE_INTEGER")

        if fast_period <= 0:
            raise ValueError("FAST_PERIOD_MUST_BE_POSITIVE")

        if slow_period <= fast_period:
            raise ValueError("SLOW_PERIOD_MUST_EXCEED_FAST_PERIOD")

        if quantity <= 0.0:
            raise ValueError("QUANTITY_MUST_BE_POSITIVE")

        if leverage <= 0:
            raise ValueError("LEVERAGE_MUST_BE_POSITIVE")

        if not 0.0 < stop_loss_percent < 1.0:
            raise ValueError("STOP_LOSS_PERCENT_MUST_BE_BETWEEN_0_AND_1")

        if not 0.0 < take_profit_percent < 1.0:
            raise ValueError("TAKE_PROFIT_PERCENT_MUST_BE_BETWEEN_0_AND_1")

        if not 0.0 <= confidence <= 100.0:
            raise ValueError("CONFIDENCE_MUST_BE_BETWEEN_0_AND_100")

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.quantity = float(quantity)
        self.leverage = leverage
        self.stop_loss_percent = float(stop_loss_percent)
        self.take_profit_percent = float(take_profit_percent)
        self.confidence = float(confidence)

        self._closes: dict[
            str,
            deque[float],
        ] = defaultdict(lambda: deque(maxlen=self.slow_period))

        self._previous_relation: dict[
            str,
            int,
        ] = {}

    def on_candle(
        self,
        context: ReplayStrategyContext,
    ) -> ReplayTradeSignal | None:
        symbol = context.candle.symbol
        close = context.candle.close

        closes = self._closes[symbol]
        closes.append(close)

        if len(closes) < self.slow_period:
            return None

        if context.has_open_position:
            self._previous_relation[symbol] = self._relation(closes)
            return None

        relation = self._relation(closes)
        previous_relation = self._previous_relation.get(symbol)

        self._previous_relation[symbol] = relation

        if previous_relation is None:
            return None

        if previous_relation <= 0 and relation > 0:
            return ReplayTradeSignal(
                symbol=symbol,
                side=PositionSide.LONG,
                confidence=self.confidence,
                quantity=self.quantity,
                leverage=self.leverage,
                stop_loss=round(
                    close * (1.0 - self.stop_loss_percent),
                    12,
                ),
                take_profit=round(
                    close * (1.0 + self.take_profit_percent),
                    12,
                ),
                reason="FAST_MA_CROSSED_ABOVE_SLOW_MA",
            )

        if previous_relation >= 0 and relation < 0:
            return ReplayTradeSignal(
                symbol=symbol,
                side=PositionSide.SHORT,
                confidence=self.confidence,
                quantity=self.quantity,
                leverage=self.leverage,
                stop_loss=round(
                    close * (1.0 + self.stop_loss_percent),
                    12,
                ),
                take_profit=round(
                    close * (1.0 - self.take_profit_percent),
                    12,
                ),
                reason="FAST_MA_CROSSED_BELOW_SLOW_MA",
            )

        return None

    def _relation(
        self,
        closes: deque[float],
    ) -> int:
        values = tuple(closes)

        fast_average = sum(values[-self.fast_period :]) / self.fast_period

        slow_average = sum(values) / self.slow_period

        if fast_average > slow_average:
            return 1

        if fast_average < slow_average:
            return -1

        return 0

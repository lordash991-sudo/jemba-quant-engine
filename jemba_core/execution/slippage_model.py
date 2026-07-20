from __future__ import annotations

import math
import random
from dataclasses import dataclass

from jemba_core.execution.execution_request import (
    OrderSide,
    VolatilityRegime,
)


@dataclass(frozen=True, slots=True)
class SlippageResult:
    rate: float
    amount: float
    executed_price: float


class SlippageModel:
    DEFAULT_RANGES = {
        VolatilityRegime.LOW: (0.0001, 0.0003),
        VolatilityRegime.MEDIUM: (0.0003, 0.0008),
        VolatilityRegime.HIGH: (0.0008, 0.0020),
        VolatilityRegime.EXTREME: (0.0020, 0.0050),
    }

    def __init__(self, seed: int | None = None) -> None:
        if seed is not None and not isinstance(seed, int):
            raise TypeError("SEED_MUST_BE_INTEGER_OR_NONE")

        self._rng = random.Random(seed)

    def calculate(
        self,
        *,
        price: float,
        side: OrderSide,
        volatility: VolatilityRegime,
    ) -> SlippageResult:
        if not math.isfinite(price):
            raise ValueError("PRICE_MUST_BE_FINITE")

        if price <= 0.0:
            raise ValueError("PRICE_MUST_BE_POSITIVE")

        if not isinstance(side, OrderSide):
            raise TypeError("SIDE_MUST_BE_ORDER_SIDE")

        if not isinstance(volatility, VolatilityRegime):
            raise TypeError("VOLATILITY_MUST_BE_VOLATILITY_REGIME")

        minimum, maximum = self.DEFAULT_RANGES[volatility]
        rate = self._rng.uniform(minimum, maximum)
        amount = price * rate

        if side is OrderSide.BUY:
            executed_price = price + amount
        else:
            executed_price = price - amount

        return SlippageResult(
            rate=float(rate),
            amount=float(amount),
            executed_price=float(executed_price),
        )

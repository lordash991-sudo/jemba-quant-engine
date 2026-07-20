from __future__ import annotations

import math
from dataclasses import dataclass

from jemba_core.execution.execution_request import OrderType


@dataclass(frozen=True, slots=True)
class CommissionResult:
    trading_fee: float
    funding_fee: float
    total_cost: float


class CommissionModel:
    def __init__(
        self,
        *,
        maker_rate: float = 0.0002,
        taker_rate: float = 0.0005,
        funding_rate: float = 0.0,
    ) -> None:
        self.maker_rate = self._validate_rate(
            maker_rate,
            "MAKER_RATE",
        )
        self.taker_rate = self._validate_rate(
            taker_rate,
            "TAKER_RATE",
        )
        self.funding_rate = self._validate_rate(
            funding_rate,
            "FUNDING_RATE",
        )

    def calculate(
        self,
        *,
        notional: float,
        order_type: OrderType,
        funding_periods: int = 0,
    ) -> CommissionResult:
        if not math.isfinite(notional):
            raise ValueError("NOTIONAL_MUST_BE_FINITE")

        if notional < 0.0:
            raise ValueError("NOTIONAL_MUST_BE_NON_NEGATIVE")

        if not isinstance(order_type, OrderType):
            raise TypeError("ORDER_TYPE_MUST_BE_ORDER_TYPE")

        if not isinstance(funding_periods, int):
            raise TypeError("FUNDING_PERIODS_MUST_BE_INTEGER")

        if funding_periods < 0:
            raise ValueError("FUNDING_PERIODS_MUST_BE_NON_NEGATIVE")

        fee_rate = self.maker_rate if order_type is OrderType.LIMIT else self.taker_rate

        trading_fee = notional * fee_rate
        funding_fee = notional * self.funding_rate * funding_periods

        return CommissionResult(
            trading_fee=float(trading_fee),
            funding_fee=float(funding_fee),
            total_cost=float(trading_fee + funding_fee),
        )

    @staticmethod
    def _validate_rate(
        value: float,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{name}_MUST_BE_NUMERIC") from exc

        if not math.isfinite(numeric):
            raise ValueError(f"{name}_MUST_BE_FINITE")

        if numeric < 0.0:
            raise ValueError(f"{name}_MUST_BE_NON_NEGATIVE")

        return numeric

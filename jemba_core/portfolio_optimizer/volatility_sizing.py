from __future__ import annotations

import math


def volatility_position_size(
    equity: float,
    risk_fraction: float,
    atr: float,
    stop_multiplier: float,
    *,
    point_value: float = 1.0,
    round_down: bool = False,
) -> float:

    if equity <= 0:
        raise ValueError("EQUITY_MUST_BE_POSITIVE")

    if not 0 < risk_fraction <= 1:
        raise ValueError("RISK_FRACTION_INVALID")

    if atr <= 0:
        raise ValueError("ATR_MUST_BE_POSITIVE")

    if stop_multiplier <= 0:
        raise ValueError("STOP_MULTIPLIER_MUST_BE_POSITIVE")

    if point_value <= 0:
        raise ValueError("POINT_VALUE_MUST_BE_POSITIVE")

    risk_amount = equity * risk_fraction

    stop_distance = atr * stop_multiplier

    size = risk_amount / (stop_distance * point_value)

    if round_down:
        size = math.floor(size)

    return float(size)

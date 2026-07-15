from __future__ import annotations

import math


def fixed_fractional_risk_amount(
    equity: float,
    risk_fraction: float,
) -> float:
    if not math.isfinite(equity):
        raise ValueError("EQUITY_MUST_BE_FINITE")

    if equity <= 0.0:
        raise ValueError("EQUITY_MUST_BE_POSITIVE")

    if not math.isfinite(risk_fraction):
        raise ValueError("RISK_FRACTION_MUST_BE_FINITE")

    if not 0.0 < risk_fraction <= 1.0:
        raise ValueError("RISK_FRACTION_MUST_BE_BETWEEN_0_EXCLUSIVE_AND_1")

    return float(equity * risk_fraction)


def fixed_fractional_position_size(
    equity: float,
    risk_fraction: float,
    stop_distance: float,
    *,
    point_value: float = 1.0,
) -> float:
    if not math.isfinite(stop_distance):
        raise ValueError("STOP_DISTANCE_MUST_BE_FINITE")

    if stop_distance <= 0.0:
        raise ValueError("STOP_DISTANCE_MUST_BE_POSITIVE")

    if not math.isfinite(point_value):
        raise ValueError("POINT_VALUE_MUST_BE_FINITE")

    if point_value <= 0.0:
        raise ValueError("POINT_VALUE_MUST_BE_POSITIVE")

    risk_amount = fixed_fractional_risk_amount(
        equity,
        risk_fraction,
    )

    return float(risk_amount / (stop_distance * point_value))

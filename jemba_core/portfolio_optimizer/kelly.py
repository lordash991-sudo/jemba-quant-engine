from __future__ import annotations

import math


def kelly_fraction(
    win_rate: float,
    payoff_ratio: float,
    *,
    fraction: float = 1.0,
    maximum: float = 1.0,
) -> float:
    if not math.isfinite(win_rate):
        raise ValueError("WIN_RATE_MUST_BE_FINITE")

    if not 0.0 <= win_rate <= 1.0:
        raise ValueError("WIN_RATE_MUST_BE_BETWEEN_0_AND_1")

    if not math.isfinite(payoff_ratio):
        raise ValueError("PAYOFF_RATIO_MUST_BE_FINITE")

    if payoff_ratio <= 0.0:
        raise ValueError("PAYOFF_RATIO_MUST_BE_POSITIVE")

    if not math.isfinite(fraction):
        raise ValueError("FRACTION_MUST_BE_FINITE")

    if not 0.0 <= fraction <= 1.0:
        raise ValueError("FRACTION_MUST_BE_BETWEEN_0_AND_1")

    if not math.isfinite(maximum):
        raise ValueError("MAXIMUM_MUST_BE_FINITE")

    if not 0.0 <= maximum <= 1.0:
        raise ValueError("MAXIMUM_MUST_BE_BETWEEN_0_AND_1")

    loss_rate = 1.0 - win_rate
    full_kelly = win_rate - (loss_rate / payoff_ratio)
    adjusted = max(0.0, full_kelly) * fraction

    return float(min(adjusted, maximum))

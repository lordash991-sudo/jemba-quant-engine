from __future__ import annotations

from jemba_core.risk.atr_stop import (
    normalize_side,
    positive_finite_price,
)


def chandelier_long(
    highest_high: float,
    atr: float,
    multiplier: float = 3.0,
) -> float:
    """Calculate a long Chandelier Exit."""
    high = positive_finite_price(
        highest_high,
        name="HIGHEST_HIGH",
    )
    atr_value = positive_finite_price(
        atr,
        name="ATR",
    )
    multiplier_value = positive_finite_price(
        multiplier,
        name="MULTIPLIER",
    )

    stop = high - atr_value * multiplier_value

    if stop < 0.0:
        raise ValueError("LONG_STOP_CANNOT_BE_NEGATIVE")

    return float(stop)


def chandelier_short(
    lowest_low: float,
    atr: float,
    multiplier: float = 3.0,
) -> float:
    """Calculate a short Chandelier Exit."""
    low = positive_finite_price(
        lowest_low,
        name="LOWEST_LOW",
    )
    atr_value = positive_finite_price(
        atr,
        name="ATR",
    )
    multiplier_value = positive_finite_price(
        multiplier,
        name="MULTIPLIER",
    )

    return float(low + atr_value * multiplier_value)


def chandelier_exit(
    reference_price: float,
    atr: float,
    multiplier: float,
    side: str,
) -> float:
    """
    Calculate a Chandelier Exit.

    For long positions, reference_price must be the highest high.
    For short positions, reference_price must be the lowest low.
    """
    normalized_side = normalize_side(side)

    if normalized_side == "long":
        return chandelier_long(
            highest_high=reference_price,
            atr=atr,
            multiplier=multiplier,
        )

    return chandelier_short(
        lowest_low=reference_price,
        atr=atr,
        multiplier=multiplier,
    )

from __future__ import annotations

import math

from jemba_core.risk.atr_stop import (
    normalize_side,
    positive_finite_price,
)


def trailing_long(
    current_stop: float,
    highest_price: float,
    atr: float,
    multiplier: float = 2.0,
) -> float:
    """
    Update a long ATR trailing stop.

    A long stop may only rise or remain unchanged.
    """
    stop = _finite_non_negative(
        current_stop,
        name="CURRENT_STOP",
    )
    high = positive_finite_price(
        highest_price,
        name="HIGHEST_PRICE",
    )
    atr_value = positive_finite_price(
        atr,
        name="ATR",
    )
    multiplier_value = positive_finite_price(
        multiplier,
        name="MULTIPLIER",
    )

    candidate = high - atr_value * multiplier_value

    if candidate < 0.0:
        candidate = 0.0

    return float(max(stop, candidate))


def trailing_short(
    current_stop: float,
    lowest_price: float,
    atr: float,
    multiplier: float = 2.0,
) -> float:
    """
    Update a short ATR trailing stop.

    A short stop may only fall or remain unchanged.
    """
    stop = positive_finite_price(
        current_stop,
        name="CURRENT_STOP",
    )
    low = positive_finite_price(
        lowest_price,
        name="LOWEST_PRICE",
    )
    atr_value = positive_finite_price(
        atr,
        name="ATR",
    )
    multiplier_value = positive_finite_price(
        multiplier,
        name="MULTIPLIER",
    )

    candidate = low + atr_value * multiplier_value

    return float(min(stop, candidate))


def update_trailing_stop(
    current_stop: float,
    reference_price: float,
    atr: float,
    multiplier: float,
    side: str,
) -> float:
    """
    Update an ATR trailing stop without allowing adverse movement.

    For long positions, reference_price is the highest favorable price.
    For short positions, reference_price is the lowest favorable price.
    """
    normalized_side = normalize_side(side)

    if normalized_side == "long":
        return trailing_long(
            current_stop=current_stop,
            highest_price=reference_price,
            atr=atr,
            multiplier=multiplier,
        )

    return trailing_short(
        current_stop=current_stop,
        lowest_price=reference_price,
        atr=atr,
        multiplier=multiplier,
    )


def _finite_non_negative(
    value: float,
    *,
    name: str,
) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError("VALUE_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name}_MUST_BE_FINITE")

    if numeric < 0.0:
        raise ValueError(f"{name}_MUST_BE_NON_NEGATIVE")

    return numeric

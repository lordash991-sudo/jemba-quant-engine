from __future__ import annotations

import math
from typing import Literal

Side = Literal["long", "short"]


def atr_stop(
    entry_price: float,
    atr: float,
    multiplier: float,
    side: str,
) -> float:
    """
    Calculate a volatility-adjusted stop-loss price.

    For a long position:

        stop = entry_price - (atr * multiplier)

    For a short position:

        stop = entry_price + (atr * multiplier)

    Parameters
    ----------
    entry_price:
        Position entry price.
    atr:
        Average True Range value.
    multiplier:
        Number of ATR units used as stop distance.
    side:
        Position direction. Accepted values are ``long`` and ``short``.
        The comparison is case-insensitive.

    Returns
    -------
    float
        Calculated stop-loss price.

    Raises
    ------
    ValueError
        If a numeric argument is invalid or the side is unsupported.
    """
    entry = _positive_finite(
        entry_price,
        finite_error="ENTRY_PRICE_MUST_BE_FINITE",
        positive_error="ENTRY_PRICE_MUST_BE_POSITIVE",
    )
    atr_value = _positive_finite(
        atr,
        finite_error="ATR_MUST_BE_FINITE",
        positive_error="ATR_MUST_BE_POSITIVE",
    )
    multiplier_value = _positive_finite(
        multiplier,
        finite_error="MULTIPLIER_MUST_BE_FINITE",
        positive_error="MULTIPLIER_MUST_BE_POSITIVE",
    )

    normalized_side = _normalize_side(side)
    stop_distance = atr_value * multiplier_value

    if normalized_side == "long":
        stop_price = entry - stop_distance

        if stop_price < 0.0:
            raise ValueError("LONG_STOP_CANNOT_BE_NEGATIVE")

        return float(stop_price)

    return float(entry + stop_distance)


def atr_stop_distance(
    atr: float,
    multiplier: float,
) -> float:
    """Return the monetary or price distance represented by the ATR stop."""
    atr_value = _positive_finite(
        atr,
        finite_error="ATR_MUST_BE_FINITE",
        positive_error="ATR_MUST_BE_POSITIVE",
    )
    multiplier_value = _positive_finite(
        multiplier,
        finite_error="MULTIPLIER_MUST_BE_FINITE",
        positive_error="MULTIPLIER_MUST_BE_POSITIVE",
    )

    return float(atr_value * multiplier_value)


def _normalize_side(side: str) -> Side:
    if not isinstance(side, str):
        raise TypeError("SIDE_MUST_BE_STRING")

    normalized = side.strip().lower()

    if normalized not in {"long", "short"}:
        raise ValueError("INVALID_SIDE")

    return normalized  # type: ignore[return-value]


def _positive_finite(
    value: float,
    *,
    finite_error: str,
    positive_error: str,
) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError("VALUE_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(finite_error)

    if numeric <= 0.0:
        raise ValueError(positive_error)

    return numeric

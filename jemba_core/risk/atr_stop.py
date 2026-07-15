from __future__ import annotations

import math
from typing import Literal, cast

Side = Literal["long", "short"]


def atr_long_stop(
    entry_price: float,
    atr: float,
    multiplier: float = 2.0,
) -> float:
    """Calculate an ATR stop below a long entry price."""
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

    stop = entry - atr_value * multiplier_value

    if stop < 0.0:
        raise ValueError("LONG_STOP_CANNOT_BE_NEGATIVE")

    return float(stop)


def atr_short_stop(
    entry_price: float,
    atr: float,
    multiplier: float = 2.0,
) -> float:
    """Calculate an ATR stop above a short entry price."""
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

    return float(entry + atr_value * multiplier_value)


def atr_stop(
    entry_price: float,
    atr: float,
    multiplier: float,
    side: str,
) -> float:
    """Calculate a long or short ATR stop."""
    normalized_side = normalize_side(side)

    if normalized_side == "long":
        return atr_long_stop(
            entry_price=entry_price,
            atr=atr,
            multiplier=multiplier,
        )

    return atr_short_stop(
        entry_price=entry_price,
        atr=atr,
        multiplier=multiplier,
    )


def atr_stop_distance(
    atr: float,
    multiplier: float = 2.0,
) -> float:
    """Return the stop distance represented by ATR times multiplier."""
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


def normalize_side(side: str) -> Side:
    """Normalize and validate a position side."""
    if not isinstance(side, str):
        raise TypeError("SIDE_MUST_BE_STRING")

    normalized = side.strip().lower()

    if normalized not in {"long", "short"}:
        raise ValueError("INVALID_SIDE")

    return cast(Side, normalized)


def positive_finite_price(
    value: float,
    *,
    name: str = "PRICE",
) -> float:
    """Validate a finite positive price-like value."""
    return _positive_finite(
        value,
        finite_error=f"{name}_MUST_BE_FINITE",
        positive_error=f"{name}_MUST_BE_POSITIVE",
    )


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

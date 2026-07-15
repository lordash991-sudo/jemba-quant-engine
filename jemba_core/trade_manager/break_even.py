from __future__ import annotations


def move_stop_to_break_even(
    entry_price: float,
    stop_price: float,
    current_price: float,
    trigger_r: float = 1.0,
) -> float:
    """
    Move stop loss to entry once the trade reaches trigger_r.

    Returns:
        New stop price.
    """

    if trigger_r <= 0:
        raise ValueError("TRIGGER_R_MUST_BE_POSITIVE")

    risk = abs(entry_price - stop_price)

    if risk <= 0:
        raise ValueError("INVALID_INITIAL_STOP")

    if entry_price > stop_price:
        reward = current_price - entry_price
    else:
        reward = entry_price - current_price

    achieved_r = reward / risk

    if achieved_r >= trigger_r:
        return float(entry_price)

    return float(stop_price)

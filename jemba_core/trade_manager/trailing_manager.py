from __future__ import annotations


def update_trailing_stop(
    current_stop: float,
    candidate_stop: float,
    side: str,
) -> float:
    """
    Never worsen the stop.

    long:
        stop only moves upward

    short:
        stop only moves downward
    """

    side = side.lower()

    if side not in ("long", "short"):
        raise ValueError("INVALID_SIDE")

    if side == "long":
        return float(max(current_stop, candidate_stop))

    return float(min(current_stop, candidate_stop))

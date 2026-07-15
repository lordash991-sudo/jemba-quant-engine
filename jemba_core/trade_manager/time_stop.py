from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class TimeStopResult:
    should_close: bool
    reason: str | None = None


def check_time_stop(
    opened_at: datetime,
    current_time: datetime,
    *,
    max_minutes: int | None = None,
    max_bars: int | None = None,
    bars_elapsed: int | None = None,
) -> TimeStopResult:
    """
    Determina si una posición debe cerrarse por tiempo.
    """

    if current_time < opened_at:
        raise ValueError("CURRENT_TIME_BEFORE_OPEN")

    if max_minutes is not None:
        if max_minutes <= 0:
            raise ValueError("MAX_MINUTES_MUST_BE_POSITIVE")

        elapsed = current_time - opened_at

        if elapsed >= timedelta(minutes=max_minutes):
            return TimeStopResult(True, "TIME_STOP")

    if max_bars is not None:
        if bars_elapsed is None:
            raise ValueError("BARS_ELAPSED_REQUIRED")

        if max_bars <= 0:
            raise ValueError("MAX_BARS_MUST_BE_POSITIVE")

        if bars_elapsed >= max_bars:
            return TimeStopResult(True, "BAR_STOP")

    return TimeStopResult(False)

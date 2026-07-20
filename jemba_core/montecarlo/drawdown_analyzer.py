from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import fmean


@dataclass(frozen=True, slots=True)
class DrawdownEpisode:
    start_index: int
    trough_index: int
    recovery_index: int | None
    depth: float
    duration: int
    recovery_duration: int | None


@dataclass(frozen=True, slots=True)
class DrawdownStats:
    max_drawdown: float
    average_drawdown: float
    max_duration: int
    max_recovery_duration: int | None
    episode_count: int
    episodes: tuple[DrawdownEpisode, ...]


class DrawdownAnalyzer:
    """Analyze drawdown depth, duration, and recovery."""

    def analyze(
        self,
        equity_curve: Sequence[float],
    ) -> DrawdownStats:
        values = _validate_equity_curve(equity_curve)

        peak_value = values[0]
        peak_index = 0

        active_start: int | None = None
        trough_index: int | None = None
        trough_depth = 0.0

        episodes: list[DrawdownEpisode] = []

        for index, equity in enumerate(values):
            if equity >= peak_value:
                if active_start is not None and trough_index is not None:
                    episodes.append(
                        DrawdownEpisode(
                            start_index=active_start,
                            trough_index=trough_index,
                            recovery_index=index,
                            depth=trough_depth,
                            duration=index - active_start,
                            recovery_duration=index - trough_index,
                        )
                    )

                    active_start = None
                    trough_index = None
                    trough_depth = 0.0

                peak_value = equity
                peak_index = index
                continue

            current_drawdown = (peak_value - equity) / peak_value

            if active_start is None:
                active_start = peak_index

            if current_drawdown > trough_depth:
                trough_depth = current_drawdown
                trough_index = index

        if active_start is not None and trough_index is not None:
            episodes.append(
                DrawdownEpisode(
                    start_index=active_start,
                    trough_index=trough_index,
                    recovery_index=None,
                    depth=trough_depth,
                    duration=(len(values) - 1) - active_start,
                    recovery_duration=None,
                )
            )

        if not episodes:
            return DrawdownStats(
                max_drawdown=0.0,
                average_drawdown=0.0,
                max_duration=0,
                max_recovery_duration=0,
                episode_count=0,
                episodes=(),
            )

        depths = tuple(episode.depth for episode in episodes)

        recovered_durations = tuple(
            episode.recovery_duration
            for episode in episodes
            if episode.recovery_duration is not None
        )

        return DrawdownStats(
            max_drawdown=float(max(depths)),
            average_drawdown=float(fmean(depths)),
            max_duration=max(episode.duration for episode in episodes),
            max_recovery_duration=(
                max(recovered_durations) if recovered_durations else None
            ),
            episode_count=len(episodes),
            episodes=tuple(episodes),
        )

    def analyze_many(
        self,
        equity_curves: Sequence[Sequence[float]],
    ) -> tuple[DrawdownStats, ...]:
        if isinstance(equity_curves, (str, bytes)):
            raise TypeError("EQUITY_CURVES_MUST_BE_SEQUENCE")

        try:
            curves = tuple(equity_curves)
        except TypeError as exc:
            raise TypeError("EQUITY_CURVES_MUST_BE_SEQUENCE") from exc

        if not curves:
            raise ValueError("EQUITY_CURVES_CANNOT_BE_EMPTY")

        return tuple(self.analyze(curve) for curve in curves)

    def percentile_max_drawdown(
        self,
        stats: Sequence[DrawdownStats],
        percentile: float,
    ) -> float:
        values = tuple(item.max_drawdown for item in stats)

        if not values:
            raise ValueError("DRAWDOWN_STATS_CANNOT_BE_EMPTY")

        return _nearest_rank_percentile(
            values,
            percentile,
        )


def _validate_equity_curve(
    equity_curve: Sequence[float],
) -> tuple[float, ...]:
    if isinstance(equity_curve, (str, bytes)):
        raise TypeError("EQUITY_CURVE_MUST_BE_NUMERIC_SEQUENCE")

    try:
        values = tuple(float(value) for value in equity_curve)
    except (TypeError, ValueError) as exc:
        raise TypeError("EQUITY_CURVE_MUST_BE_NUMERIC_SEQUENCE") from exc

    if not values:
        raise ValueError("EQUITY_CURVE_CANNOT_BE_EMPTY")

    for value in values:
        if not math.isfinite(value):
            raise ValueError("EQUITY_VALUE_MUST_BE_FINITE")

        if value <= 0.0:
            raise ValueError("EQUITY_VALUE_MUST_BE_POSITIVE")

    return values


def _nearest_rank_percentile(
    values: Sequence[float],
    percentile: float,
) -> float:
    if not math.isfinite(percentile):
        raise ValueError("PERCENTILE_MUST_BE_FINITE")

    if not 0.0 <= percentile <= 100.0:
        raise ValueError("PERCENTILE_MUST_BE_BETWEEN_0_AND_100")

    ordered = sorted(float(value) for value in values)

    if percentile == 0.0:
        return ordered[0]

    rank = math.ceil(percentile / 100.0 * len(ordered))

    return ordered[rank - 1]

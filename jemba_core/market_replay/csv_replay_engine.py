from __future__ import annotations

from collections.abc import Callable, Iterable

from jemba_core.market_replay.csv_loader import CSVMarketLoader
from jemba_core.market_replay.models import (
    Candle,
    ReplayConfig,
    ReplayEvent,
    ReplaySnapshot,
    ReplaySource,
    ReplayStatistics,
    ReplayStatus,
)
from jemba_core.market_replay.replay_clock import ReplayClock

ReplayCallback = Callable[[ReplayEvent], None]


class CSVReplayEngine:
    """
    Deterministic chronological replay of one or more CSV sources.

    It emits candles in global timestamp order. Consumers may connect
    PaperTradingSession, indicators, predictors, metrics, or reports.
    """

    def __init__(
        self,
        sources: Iterable[ReplaySource],
        *,
        config: ReplayConfig | None = None,
        loader: CSVMarketLoader | None = None,
    ) -> None:
        if isinstance(sources, (str, bytes)):
            raise TypeError("SOURCES_MUST_BE_ITERABLE")

        self.sources = tuple(sources)

        if not self.sources:
            raise ValueError("SOURCES_CANNOT_BE_EMPTY")

        if not all(isinstance(source, ReplaySource) for source in self.sources):
            raise TypeError("ALL_SOURCES_MUST_BE_REPLAY_SOURCE")

        self.config = config or ReplayConfig()
        self.loader = loader or CSVMarketLoader()
        self.clock = ReplayClock(self.config.speed)

        self.status = ReplayStatus.CREATED
        self._candles: tuple[Candle, ...] = ()
        self._cursor = 0
        self._callbacks: list[ReplayCallback] = []
        self._current_candle: Candle | None = None

    def load(self) -> ReplaySnapshot:
        if self.status is ReplayStatus.RUNNING:
            raise ValueError("CANNOT_LOAD_WHILE_RUNNING")

        self._candles = self.loader.load_many(
            self.sources,
            config=self.config,
        )

        self._cursor = 0
        self._current_candle = None
        self.clock.reset()
        self.status = ReplayStatus.READY

        return self.snapshot()

    def subscribe(
        self,
        callback: ReplayCallback,
    ) -> None:
        if not callable(callback):
            raise TypeError("CALLBACK_MUST_BE_CALLABLE")

        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(
        self,
        callback: ReplayCallback,
    ) -> None:
        try:
            self._callbacks.remove(callback)
        except ValueError:
            pass

    def play(
        self,
        *,
        maximum_events: int | None = None,
    ) -> tuple[ReplayEvent, ...]:
        if self.status is ReplayStatus.CREATED:
            self.load()

        if self.status is ReplayStatus.COMPLETED:
            return ()

        if self.status is ReplayStatus.STOPPED:
            raise ValueError("STOPPED_REPLAY_MUST_BE_RESET")

        if maximum_events is not None:
            if not isinstance(maximum_events, int):
                raise TypeError("MAXIMUM_EVENTS_MUST_BE_INTEGER")

            if maximum_events <= 0:
                raise ValueError("MAXIMUM_EVENTS_MUST_BE_POSITIVE")

        self.status = ReplayStatus.RUNNING

        emitted: list[ReplayEvent] = []

        while self.status is ReplayStatus.RUNNING:
            if maximum_events is not None and len(emitted) >= maximum_events:
                break

            event = self.step()

            if event is None:
                break

            emitted.append(event)

        return tuple(emitted)

    def step(self) -> ReplayEvent | None:
        if self.status is ReplayStatus.CREATED:
            self.load()

        if self.status is ReplayStatus.PAUSED:
            return None

        if self.status in (
            ReplayStatus.STOPPED,
            ReplayStatus.COMPLETED,
        ):
            return None

        if self.status is ReplayStatus.READY:
            self.status = ReplayStatus.RUNNING

        if self._cursor >= len(self._candles):
            self.status = ReplayStatus.COMPLETED
            return None

        candle = self._candles[self._cursor]
        self.clock.advance(candle.timestamp)

        event = ReplayEvent(
            index=self._cursor,
            candle=candle,
        )

        self._cursor += 1
        self._current_candle = candle

        for callback in tuple(self._callbacks):
            callback(event)

        if self._cursor >= len(self._candles):
            self.status = ReplayStatus.COMPLETED

        return event

    def pause(self) -> ReplaySnapshot:
        if self.status is not ReplayStatus.RUNNING:
            raise ValueError("REPLAY_MUST_BE_RUNNING_TO_PAUSE")

        self.status = ReplayStatus.PAUSED
        return self.snapshot()

    def resume(
        self,
        *,
        maximum_events: int | None = None,
    ) -> tuple[ReplayEvent, ...]:
        if self.status is not ReplayStatus.PAUSED:
            raise ValueError("REPLAY_MUST_BE_PAUSED_TO_RESUME")

        self.status = ReplayStatus.RUNNING

        return self.play(maximum_events=maximum_events)

    def stop(self) -> ReplaySnapshot:
        if self.status in (
            ReplayStatus.STOPPED,
            ReplayStatus.COMPLETED,
        ):
            return self.snapshot()

        self.status = ReplayStatus.STOPPED
        return self.snapshot()

    def reset(self) -> ReplaySnapshot:
        self._cursor = 0
        self._current_candle = None
        self.clock.reset()

        self.status = ReplayStatus.READY if self._candles else ReplayStatus.CREATED

        return self.snapshot()

    def seek(
        self,
        index: int,
    ) -> ReplaySnapshot:
        if not isinstance(index, int):
            raise TypeError("INDEX_MUST_BE_INTEGER")

        if not 0 <= index <= len(self._candles):
            raise ValueError("INDEX_OUT_OF_RANGE")

        self._cursor = index
        self._current_candle = self._candles[index - 1] if index > 0 else None

        self.clock.reset()

        if self._current_candle is not None:
            self.clock.advance(self._current_candle.timestamp)

        self.status = (
            ReplayStatus.COMPLETED
            if index == len(self._candles)
            else ReplayStatus.READY
        )

        return self.snapshot()

    def statistics(self) -> ReplayStatistics:
        first_timestamp = self._candles[0].timestamp if self._candles else None

        last_timestamp = self._candles[-1].timestamp if self._candles else None

        symbols = tuple(sorted({candle.symbol for candle in self._candles}))

        return ReplayStatistics(
            total_sources=len(self.sources),
            total_candles=len(self._candles),
            processed_candles=self._cursor,
            remaining_candles=(len(self._candles) - self._cursor),
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            current_timestamp=(self.clock.current_timestamp),
            symbols=symbols,
        )

    def snapshot(self) -> ReplaySnapshot:
        statistics = self.statistics()

        return ReplaySnapshot(
            status=self.status,
            speed=self.clock.speed,
            cursor=self._cursor,
            total_candles=len(self._candles),
            current_timestamp=(self.clock.current_timestamp),
            current_symbol=(
                self._current_candle.symbol
                if self._current_candle is not None
                else None
            ),
            statistics=statistics,
        )

    @property
    def candles(self) -> tuple[Candle, ...]:
        return self._candles

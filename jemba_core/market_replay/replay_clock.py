from __future__ import annotations

from datetime import datetime

from jemba_core.market_replay.models import ReplaySpeed


class ReplayClock:
    SPEED_MULTIPLIERS = {
        ReplaySpeed.X1: 1,
        ReplaySpeed.X5: 5,
        ReplaySpeed.X20: 20,
        ReplaySpeed.X100: 100,
        ReplaySpeed.X1000: 1000,
    }

    def __init__(
        self,
        speed: ReplaySpeed = ReplaySpeed.X1000,
    ) -> None:
        self.set_speed(speed)
        self.current_timestamp: datetime | None = None

    @property
    def multiplier(self) -> int:
        return self.SPEED_MULTIPLIERS[self.speed]

    def set_speed(
        self,
        speed: ReplaySpeed,
    ) -> None:
        if not isinstance(speed, ReplaySpeed):
            raise TypeError("SPEED_MUST_BE_REPLAY_SPEED")

        self.speed = speed

    def advance(
        self,
        timestamp: datetime,
    ) -> datetime:
        if timestamp.tzinfo is None:
            raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")

        if self.current_timestamp is not None and timestamp < self.current_timestamp:
            raise ValueError("REPLAY_CLOCK_CANNOT_MOVE_BACKWARD")

        self.current_timestamp = timestamp
        return timestamp

    def reset(self) -> None:
        self.current_timestamp = None

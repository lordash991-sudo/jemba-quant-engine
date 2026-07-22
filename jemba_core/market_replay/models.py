from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, time
from enum import StrEnum
from pathlib import Path


class ReplayStatus(StrEnum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"


class ReplaySpeed(StrEnum):
    X1 = "1X"
    X5 = "5X"
    X20 = "20X"
    X100 = "100X"
    X1000 = "1000X"


class MarketSession(StrEnum):
    ALL = "ALL"
    ASIA = "ASIA"
    LONDON = "LONDON"
    NEW_YORK = "NEW_YORK"


@dataclass(frozen=True, slots=True)
class ReplayConfig:
    speed: ReplaySpeed = ReplaySpeed.X1000
    start_at: datetime | None = None
    end_at: datetime | None = None
    market_session: MarketSession = MarketSession.ALL
    strict_csv: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.speed, ReplaySpeed):
            raise TypeError("SPEED_MUST_BE_REPLAY_SPEED")

        if not isinstance(self.market_session, MarketSession):
            raise TypeError("MARKET_SESSION_MUST_BE_MARKET_SESSION")

        if not isinstance(self.strict_csv, bool):
            raise TypeError("STRICT_CSV_MUST_BE_BOOLEAN")

        for name, value in (
            ("START_AT", self.start_at),
            ("END_AT", self.end_at),
        ):
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name}_MUST_BE_TIMEZONE_AWARE")

        if (
            self.start_at is not None
            and self.end_at is not None
            and self.end_at < self.start_at
        ):
            raise ValueError("END_AT_MUST_NOT_PRECEDE_START_AT")


@dataclass(frozen=True, slots=True)
class ReplaySource:
    symbol: str
    file_path: Path

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()

        if not symbol:
            raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

        path = Path(self.file_path)

        if path.suffix.lower() != ".csv":
            raise ValueError("SOURCE_FILE_MUST_BE_CSV")

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "file_path", path)


@dataclass(frozen=True, slots=True)
class Candle:
    symbol: str
    timestamp: datetime

    open: float
    high: float
    low: float
    close: float
    volume: float

    bid: float | None = None
    ask: float | None = None
    spread: float | None = None
    funding: float | None = None
    open_interest: float | None = None

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()

        if not symbol:
            raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

        if self.timestamp.tzinfo is None:
            raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")

        numeric_values = {
            "OPEN": self.open,
            "HIGH": self.high,
            "LOW": self.low,
            "CLOSE": self.close,
            "VOLUME": self.volume,
        }

        converted: dict[str, float] = {}

        for name, value in numeric_values.items():
            numeric = _finite_float(value, name)

            if name != "VOLUME" and numeric <= 0.0:
                raise ValueError(f"{name}_MUST_BE_POSITIVE")

            if name == "VOLUME" and numeric < 0.0:
                raise ValueError("VOLUME_MUST_BE_NON_NEGATIVE")

            converted[name] = numeric

        if converted["HIGH"] < max(
            converted["OPEN"],
            converted["CLOSE"],
            converted["LOW"],
        ):
            raise ValueError("INVALID_CANDLE_HIGH")

        if converted["LOW"] > min(
            converted["OPEN"],
            converted["CLOSE"],
            converted["HIGH"],
        ):
            raise ValueError("INVALID_CANDLE_LOW")

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "open", converted["OPEN"])
        object.__setattr__(self, "high", converted["HIGH"])
        object.__setattr__(self, "low", converted["LOW"])
        object.__setattr__(self, "close", converted["CLOSE"])
        object.__setattr__(self, "volume", converted["VOLUME"])

        for field_name in (
            "bid",
            "ask",
            "spread",
            "funding",
            "open_interest",
        ):
            value = getattr(self, field_name)

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _finite_float(
                        value,
                        field_name.upper(),
                    ),
                )


@dataclass(frozen=True, slots=True)
class ReplayEvent:
    index: int
    candle: Candle


@dataclass(frozen=True, slots=True)
class ReplayStatistics:
    total_sources: int
    total_candles: int
    processed_candles: int
    remaining_candles: int

    first_timestamp: datetime | None
    last_timestamp: datetime | None
    current_timestamp: datetime | None

    symbols: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReplaySnapshot:
    status: ReplayStatus
    speed: ReplaySpeed

    cursor: int
    total_candles: int

    current_timestamp: datetime | None
    current_symbol: str | None

    statistics: ReplayStatistics


def is_in_market_session(
    timestamp: datetime,
    session: MarketSession,
) -> bool:
    if session is MarketSession.ALL:
        return True

    utc_time = timestamp.timetz().replace(tzinfo=None)

    if session is MarketSession.ASIA:
        return time(0, 0) <= utc_time < time(8, 0)

    if session is MarketSession.LONDON:
        return time(8, 0) <= utc_time < time(13, 0)

    if session is MarketSession.NEW_YORK:
        return time(13, 0) <= utc_time < time(22, 0)

    return False


def _finite_float(
    value: float,
    name: str,
) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name}_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name}_MUST_BE_FINITE")

    return numeric

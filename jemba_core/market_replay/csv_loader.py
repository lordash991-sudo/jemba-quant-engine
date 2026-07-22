from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path

from jemba_core.market_replay.models import (
    Candle,
    ReplayConfig,
    ReplaySource,
    is_in_market_session,
)

_COLUMN_ALIASES = {
    "timestamp": (
        "timestamp",
        "time",
        "datetime",
        "date",
        "open_time",
        "opentime",
    ),
    "open": ("open", "o"),
    "high": ("high", "h"),
    "low": ("low", "l"),
    "close": ("close", "c"),
    "volume": ("volume", "vol", "v"),
    "bid": ("bid",),
    "ask": ("ask",),
    "spread": ("spread",),
    "funding": ("funding", "funding_rate"),
    "open_interest": (
        "open_interest",
        "openinterest",
        "oi",
    ),
}


class CSVMarketLoader:
    def load(
        self,
        source: ReplaySource,
        *,
        config: ReplayConfig | None = None,
    ) -> tuple[Candle, ...]:
        if not isinstance(source, ReplaySource):
            raise TypeError("SOURCE_MUST_BE_REPLAY_SOURCE")

        replay_config = config or ReplayConfig()
        path = Path(source.file_path)

        if not path.exists():
            raise FileNotFoundError(f"CSV_SOURCE_NOT_FOUND: {path}")

        candles: list[Candle] = []

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise ValueError("CSV_HAS_NO_HEADER")

            mapping = _resolve_columns(
                reader.fieldnames,
                strict=replay_config.strict_csv,
            )

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                try:
                    candle = self._row_to_candle(
                        row,
                        source=source,
                        mapping=mapping,
                    )
                except (
                    TypeError,
                    ValueError,
                    KeyError,
                ) as exc:
                    if replay_config.strict_csv:
                        raise ValueError(
                            f"INVALID_CSV_ROW_{row_number}: {exc}"
                        ) from exc

                    continue

                if not _passes_filters(
                    candle,
                    replay_config,
                ):
                    continue

                candles.append(candle)

        candles.sort(key=lambda candle: candle.timestamp)

        return tuple(candles)

    def load_many(
        self,
        sources: Iterable[ReplaySource],
        *,
        config: ReplayConfig | None = None,
    ) -> tuple[Candle, ...]:
        if isinstance(sources, (str, bytes)):
            raise TypeError("SOURCES_MUST_BE_ITERABLE")

        values = tuple(sources)

        if not values:
            raise ValueError("SOURCES_CANNOT_BE_EMPTY")

        if not all(isinstance(source, ReplaySource) for source in values):
            raise TypeError("ALL_SOURCES_MUST_BE_REPLAY_SOURCE")

        candles = [
            candle
            for source in values
            for candle in self.load(
                source,
                config=config,
            )
        ]

        candles.sort(
            key=lambda candle: (
                candle.timestamp,
                candle.symbol,
            )
        )

        return tuple(candles)

    @staticmethod
    def _row_to_candle(
        row: dict[str, str | None],
        *,
        source: ReplaySource,
        mapping: dict[str, str | None],
    ) -> Candle:
        def required(name: str) -> str:
            column = mapping[name]

            if column is None:
                raise KeyError(f"MISSING_REQUIRED_COLUMN_{name.upper()}")

            value = row.get(column)

            if value is None or not value.strip():
                raise ValueError(f"EMPTY_REQUIRED_VALUE_{name.upper()}")

            return value.strip()

        def optional(name: str) -> float | None:
            column = mapping.get(name)

            if column is None:
                return None

            value = row.get(column)

            if value is None or not value.strip():
                return None

            return float(value)

        return Candle(
            symbol=source.symbol,
            timestamp=_parse_timestamp(required("timestamp")),
            open=float(required("open")),
            high=float(required("high")),
            low=float(required("low")),
            close=float(required("close")),
            volume=float(required("volume")),
            bid=optional("bid"),
            ask=optional("ask"),
            spread=optional("spread"),
            funding=optional("funding"),
            open_interest=optional("open_interest"),
        )


def _resolve_columns(
    fieldnames: Sequence[str],
    *,
    strict: bool,
) -> dict[str, str | None]:
    normalized = {field.strip().lower(): field for field in fieldnames}

    mapping: dict[str, str | None] = {}

    for canonical, aliases in _COLUMN_ALIASES.items():
        match = next(
            (normalized[alias] for alias in aliases if alias in normalized),
            None,
        )

        mapping[canonical] = match

    required_fields = (
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )

    missing = [field for field in required_fields if mapping[field] is None]

    if strict and missing:
        raise ValueError("CSV_MISSING_COLUMNS: " + ", ".join(missing))

    return mapping


def _parse_timestamp(
    value: str,
) -> datetime:
    stripped = value.strip()

    try:
        numeric = float(stripped)
    except ValueError:
        numeric = None

    if numeric is not None:
        if numeric > 10_000_000_000:
            numeric /= 1000.0

        return datetime.fromtimestamp(
            numeric,
            tz=UTC,
        )

    normalized = stripped.replace(
        "Z",
        "+00:00",
    )

    timestamp = datetime.fromisoformat(normalized)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)

    return timestamp.astimezone(UTC)


def _passes_filters(
    candle: Candle,
    config: ReplayConfig,
) -> bool:
    if config.start_at is not None and candle.timestamp < config.start_at:
        return False

    if config.end_at is not None and candle.timestamp > config.end_at:
        return False

    return is_in_market_session(
        candle.timestamp,
        config.market_session,
    )

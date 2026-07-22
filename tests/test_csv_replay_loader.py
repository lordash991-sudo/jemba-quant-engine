from datetime import UTC, datetime

import pytest

from jemba_core.market_replay import (
    CSVMarketLoader,
    MarketSession,
    ReplayConfig,
    ReplaySource,
)


def write_csv(tmp_path):
    path = tmp_path / "BTCUSDT.csv"

    path.write_text(
        "\n".join(
            [
                "timestamp,open,high,low,close,volume",
                "2026-01-01T03:00:00Z,100,110,90,105,1000",
                "2026-01-01T09:00:00Z,105,115,100,112,1200",
                "2026-01-01T15:00:00Z,112,120,108,118,1500",
            ]
        ),
        encoding="utf-8",
    )

    return path


def test_loads_csv(tmp_path):
    path = write_csv(tmp_path)

    candles = CSVMarketLoader().load(
        ReplaySource(
            symbol="BTCUSDT",
            file_path=path,
        )
    )

    assert len(candles) == 3
    assert candles[0].close == pytest.approx(105.0)


def test_filters_market_session(tmp_path):
    path = write_csv(tmp_path)

    candles = CSVMarketLoader().load(
        ReplaySource(
            symbol="BTCUSDT",
            file_path=path,
        ),
        config=ReplayConfig(market_session=MarketSession.LONDON),
    )

    assert len(candles) == 1
    assert candles[0].timestamp.hour == 9


def test_filters_dates(tmp_path):
    path = write_csv(tmp_path)

    candles = CSVMarketLoader().load(
        ReplaySource(
            symbol="BTCUSDT",
            file_path=path,
        ),
        config=ReplayConfig(
            start_at=datetime(
                2026,
                1,
                1,
                8,
                0,
                tzinfo=UTC,
            ),
            end_at=datetime(
                2026,
                1,
                1,
                12,
                0,
                tzinfo=UTC,
            ),
        ),
    )

    assert len(candles) == 1


def test_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        CSVMarketLoader().load(
            ReplaySource(
                symbol="BTCUSDT",
                file_path=(tmp_path / "missing.csv"),
            )
        )


def test_supports_unix_milliseconds(tmp_path):
    path = tmp_path / "ETHUSDT.csv"

    path.write_text(
        "\n".join(
            [
                "timestamp,open,high,low,close,volume",
                "1767225600000,100,110,90,105,1000",
            ]
        ),
        encoding="utf-8",
    )

    candles = CSVMarketLoader().load(
        ReplaySource(
            symbol="ETHUSDT",
            file_path=path,
        )
    )

    assert len(candles) == 1
    assert candles[0].timestamp.tzinfo is not None

from jemba_core.market_replay import (
    CSVReplayEngine,
    ReplaySource,
    ReplayStatus,
)


def create_csv(
    tmp_path,
    name,
    rows,
):
    path = tmp_path / name

    path.write_text(
        "\n".join(
            [
                "timestamp,open,high,low,close,volume",
                *rows,
            ]
        ),
        encoding="utf-8",
    )

    return path


def create_engine(tmp_path):
    btc = create_csv(
        tmp_path,
        "BTCUSDT.csv",
        [
            "2026-01-01T01:00:00Z,100,110,90,105,1000",
            "2026-01-01T03:00:00Z,105,115,100,112,1200",
        ],
    )

    eth = create_csv(
        tmp_path,
        "ETHUSDT.csv",
        [
            "2026-01-01T02:00:00Z,50,55,45,53,500",
            "2026-01-01T04:00:00Z,53,60,50,58,700",
        ],
    )

    return CSVReplayEngine(
        [
            ReplaySource(
                symbol="BTCUSDT",
                file_path=btc,
            ),
            ReplaySource(
                symbol="ETHUSDT",
                file_path=eth,
            ),
        ]
    )


def test_loads_multiple_sources(tmp_path):
    engine = create_engine(tmp_path)

    snapshot = engine.load()

    assert snapshot.status is ReplayStatus.READY
    assert snapshot.total_candles == 4
    assert snapshot.statistics.symbols == (
        "BTCUSDT",
        "ETHUSDT",
    )


def test_replays_in_global_time_order(tmp_path):
    engine = create_engine(tmp_path)

    events = engine.play()

    timestamps = [event.candle.timestamp for event in events]

    assert timestamps == sorted(timestamps)
    assert engine.status is ReplayStatus.COMPLETED


def test_step(tmp_path):
    engine = create_engine(tmp_path)
    engine.load()

    event = engine.step()

    assert event is not None
    assert event.index == 0
    assert engine.snapshot().cursor == 1


def test_callback_receives_events(tmp_path):
    engine = create_engine(tmp_path)
    received = []

    engine.subscribe(received.append)
    engine.play(maximum_events=2)

    assert len(received) == 2


def test_stop_and_reset(tmp_path):
    engine = create_engine(tmp_path)

    engine.play(maximum_events=1)
    engine.stop()

    assert engine.status is ReplayStatus.STOPPED

    snapshot = engine.reset()

    assert snapshot.cursor == 0
    assert snapshot.status is ReplayStatus.READY


def test_seek(tmp_path):
    engine = create_engine(tmp_path)
    engine.load()

    snapshot = engine.seek(2)

    assert snapshot.cursor == 2
    assert snapshot.current_timestamp is not None


def test_statistics(tmp_path):
    engine = create_engine(tmp_path)
    engine.load()
    engine.step()

    stats = engine.statistics()

    assert stats.total_candles == 4
    assert stats.processed_candles == 1
    assert stats.remaining_candles == 3

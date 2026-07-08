from pathlib import Path

from jemba_core.database.sqlite_storage import SQLiteStorage


def test_create_database(tmp_path):
    db = SQLiteStorage(tmp_path / "test.db")

    db.create_tables()

    assert Path(tmp_path / "test.db").exists()


def test_insert_trade(tmp_path):
    db = SQLiteStorage(tmp_path / "test.db")

    db.create_tables()

    db.insert_trade(
        symbol="BTCUSDT",
        side="LONG",
        size=0.5,
        entry=100000,
        exit_price=101000,
        pnl=500,
    )

    trades = db.trades()

    assert len(trades) == 1
    assert trades[0]["symbol"] == "BTCUSDT"


def test_multiple_trades(tmp_path):
    db = SQLiteStorage(tmp_path / "test.db")

    db.create_tables()

    for _i in range(5):
        db.insert_trade(
            "BTCUSDT",
            "LONG",
            1,
            100,
            105,
            5,
        )

    assert len(db.trades()) == 5

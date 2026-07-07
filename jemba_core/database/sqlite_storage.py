from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteStorage:

    def __init__(self, database="database/jemba.db"):

        self.path = Path(database)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row

    def execute(self, sql, params=()):

        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        self.connection.commit()

        return cursor

    def create_tables(self):

        self.execute("""
        CREATE TABLE IF NOT EXISTS trades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            side TEXT,
            size REAL,
            entry REAL,
            exit REAL,
            pnl REAL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    def insert_trade(
        self,
        symbol,
        side,
        size,
        entry,
        exit_price,
        pnl,
    ):

        self.execute(
            """
            INSERT INTO trades
            (
                symbol,
                side,
                size,
                entry,
                exit,
                pnl
            )
            VALUES
            (?,?,?,?,?,?)
            """,
            (
                symbol,
                side,
                size,
                entry,
                exit_price,
                pnl,
            ),
        )

    def trades(self):

        cursor = self.execute(
            "SELECT * FROM trades ORDER BY id"
        )

        return cursor.fetchall()
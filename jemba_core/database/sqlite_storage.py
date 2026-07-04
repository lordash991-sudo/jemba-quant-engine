from pathlib import Path

from sqlalchemy import create_engine, text

from config.project import DATABASE_DIR


class SQLiteStorage:
    def __init__(self, database_name: str = "jemba.db"):
        self.database_path = DATABASE_DIR / database_name
        self.engine = create_engine(f"sqlite:///{self.database_path}")

    def create_tables(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS candles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    UNIQUE(symbol, timeframe, timestamp)
                )
            """))

    def save_candles(self, candles) -> int:
        if not candles:
            return 0

        inserted = 0

        with self.engine.begin() as conn:
            for candle in candles:
                result = conn.execute(
                    text("""
                        INSERT OR IGNORE INTO candles (
                            symbol,
                            timeframe,
                            timestamp,
                            open,
                            high,
                            low,
                            close,
                            volume
                        )
                        VALUES (
                            :symbol,
                            :timeframe,
                            :timestamp,
                            :open,
                            :high,
                            :low,
                            :close,
                            :volume
                        )
                    """),
                    {
                        "symbol": candle.symbol,
                        "timeframe": candle.timeframe,
                        "timestamp": candle.timestamp.isoformat(),
                        "open": candle.open,
                        "high": candle.high,
                        "low": candle.low,
                        "close": candle.close,
                        "volume": candle.volume,
                    },
                )
                inserted += result.rowcount

        return inserted

    def count_candles(self) -> int:
        with self.engine.begin() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM candles"))
            return int(result.scalar())

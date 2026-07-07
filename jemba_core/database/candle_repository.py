import pandas as pd
from sqlalchemy import text


class CandleRepository:

    def __init__(self, storage):
        self.storage = storage

    def load_candles(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        query = text("""
            SELECT
                symbol,
                timeframe,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            FROM candles
            WHERE symbol = :symbol
              AND timeframe = :timeframe
            ORDER BY timestamp DESC
            LIMIT :limit
        """)

        with self.storage.engine.begin() as conn:
            df = pd.read_sql(
                query,
                conn,
                params={
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "limit": limit,
                },
            )

        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

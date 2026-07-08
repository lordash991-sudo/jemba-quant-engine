import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.database.sqlite_storage import SQLiteStorage

storage = SQLiteStorage()

query = """
SELECT
    symbol,
    timeframe,
    COUNT(*) as candles,
    MIN(timestamp) as desde,
    MAX(timestamp) as hasta
FROM candles
GROUP BY symbol, timeframe
ORDER BY symbol
"""

df = pd.read_sql(query, storage.engine)

print()
print("RESUMEN SQLITE")
print(df)
print()
print("TOTAL VELAS:", df["candles"].sum())

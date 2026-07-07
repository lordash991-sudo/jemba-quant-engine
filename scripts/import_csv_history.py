import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.common.candle import Candle
from jemba_core.database.sqlite_storage import SQLiteStorage

DATA_DIR = Path(r"C:\Users\Jemba\OneDrive\Escritorio\JEMBA_BTC_LAB\01_DATA")


def symbol_from_filename(path):
    return path.name.split("_")[0].replace("USDT", "-USDT")


def row_to_candle(row, symbol):
    return Candle(
        symbol=symbol,
        timeframe="1h",
        timestamp=pd.to_datetime(row["datetime"]),
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=float(row["volume"])
    )


storage = SQLiteStorage()
storage.create_tables()

files = list(DATA_DIR.glob("*.csv"))

print(f"CSV encontrados: {len(files)}")

for file in files:
    symbol = symbol_from_filename(file)
    df = pd.read_csv(file)

    candles = [
        row_to_candle(row, symbol)
        for _, row in df.iterrows()
    ]

    inserted = storage.save_candles(candles)

    print(f"{symbol}: leidas={len(candles)} nuevas={inserted}")

print("IMPORTACION COMPLETA")

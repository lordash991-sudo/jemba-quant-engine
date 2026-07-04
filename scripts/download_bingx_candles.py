from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from jemba_core.providers.bingx_provider import BingXProvider
from jemba_core.database.sqlite_storage import SQLiteStorage


def main():
    provider = BingXProvider()
    storage = SQLiteStorage()

    storage.create_tables()

    candles = provider.get_candles("BTC-USDT", "1h", 100)
    inserted = storage.save_candles(candles)
    total = storage.count_candles()

    print(f"Velas descargadas: {len(candles)}")
    print(f"Velas nuevas guardadas: {inserted}")
    print(f"Total velas en base de datos: {total}")


if __name__ == "__main__":
    main()

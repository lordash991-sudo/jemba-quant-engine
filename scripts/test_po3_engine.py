import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.database.candle_repository import CandleRepository
from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.features.feature_engine import FeatureEngine
from jemba_core.po3.po3_engine import PO3Engine

storage = SQLiteStorage()
repo = CandleRepository(storage)

df = repo.load_candles("BTC-USDT", "1h", 1000)
df = FeatureEngine.generate(df)

engine = PO3Engine()
trades = engine.detect(df, "BTC-USDT", "1h")

print()
print("PO3 TRADES DETECTADOS:", len(trades))

for trade in trades[-10:]:
    print(trade)

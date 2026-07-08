import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.database.candle_repository import CandleRepository
from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.strategy.strategy_engine import StrategyEngine

storage = SQLiteStorage()
repo = CandleRepository(storage)

df = repo.load_candles("BTC-USDT", "1h", 200)

engine = StrategyEngine()

print()
print("SENAL:")
print(engine.signal(df))

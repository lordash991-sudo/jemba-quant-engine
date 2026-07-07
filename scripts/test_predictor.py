
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.ai.predictor import Predictor
from jemba_core.database.candle_repository import CandleRepository
from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.features.feature_engine import FeatureEngine

storage = SQLiteStorage()
repo = CandleRepository(storage)

df = repo.load_candles("BTC-USDT", "1h", 100)

df["EMA20"] = FeatureEngine.ema(df, 20)
df["EMA50"] = FeatureEngine.ema(df, 50)
df["ATR"] = FeatureEngine.atr(df)
df["BODY"] = FeatureEngine.body(df)
df["BULLISH"] = FeatureEngine.bullish(df)
df["BEARISH"] = FeatureEngine.bearish(df)

predictor = Predictor()

print(df.tail())
print()
print("Prediccion:")
print(predictor.predict_last(df))

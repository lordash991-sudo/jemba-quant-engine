import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import pandas as pd

from jemba_core.features.feature_engine import FeatureEngine
from jemba_core.providers.bingx_provider import BingXProvider

provider = BingXProvider()

candles = provider.get_candles(
    "BTC-USDT",
    "1h",
    50
)

df = pd.DataFrame([c.__dict__ for c in candles])

df["EMA20"] = FeatureEngine.ema(df, 20)
df["EMA50"] = FeatureEngine.ema(df, 50)
df["ATR"] = FeatureEngine.atr(df)
df["BODY"] = FeatureEngine.body(df)

print(df.tail())

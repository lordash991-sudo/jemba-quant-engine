from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.ai.dataset_builder import DatasetBuilder

builder = DatasetBuilder()

df = builder.build(
    symbol="BTC-USDT",
    timeframe="1h",
    limit=100
)

print(df.tail())
print(df.shape)

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.ai.dataset_builder import DatasetBuilder
from jemba_core.ai.label_generator import LabelGenerator

builder = DatasetBuilder()

df = builder.build(
    symbol="BTC-USDT",
    timeframe="1h",
    limit=300
)

df = LabelGenerator.generate(df)

print(df[[
    "close",
    "EMA20",
    "EMA50",
    "ATR",
    "LABEL"
]].tail(20))

print()

print(df["LABEL"].value_counts())

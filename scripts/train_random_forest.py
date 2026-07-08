import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.ai.dataset_builder import DatasetBuilder
from jemba_core.ai.label_generator import LabelGenerator
from jemba_core.ai.trainer import Trainer

builder = DatasetBuilder()

df = builder.build(symbol="BTC-USDT", timeframe="1h", limit=5000)

df = LabelGenerator.generate(df)

trainer = Trainer()

trainer.train(df)

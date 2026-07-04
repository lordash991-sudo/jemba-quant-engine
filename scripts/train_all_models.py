from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.ai.portfolio_trainer import PortfolioTrainer

trainer = PortfolioTrainer()

report = trainer.train_all()

print()
print("REPORTE FINAL")
print(report)

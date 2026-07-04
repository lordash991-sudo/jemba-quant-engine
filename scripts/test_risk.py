from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.risk.risk_manager import RiskConfig
from jemba_core.risk.risk_manager import RiskManager

cfg = RiskConfig(
    account_balance=1000,
    risk_percent=1,
    stop_loss_percent=1.5,
    take_profit_percent=3
)

risk = RiskManager(cfg)

entry = 62500

print()
print("Capital Riesgo:", risk.capital_at_risk())
print("Cantidad:", risk.position_size(entry))
print("SL:", risk.stop_loss(entry))
print("TP:", risk.take_profit(entry))

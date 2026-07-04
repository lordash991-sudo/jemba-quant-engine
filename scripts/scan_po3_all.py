from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.database.candle_repository import CandleRepository
from jemba_core.features.feature_engine import FeatureEngine
from jemba_core.po3.po3_engine import PO3Engine


storage = SQLiteStorage()
repo = CandleRepository(storage)

symbols_df = pd.read_sql(
    "SELECT DISTINCT symbol FROM candles ORDER BY symbol",
    storage.engine
)

engine = PO3Engine()

results = []

for symbol in symbols_df["symbol"].tolist():
    print()
    print(f"Escaneando {symbol}...")

    df = repo.load_candles(symbol, "1h", 30000)
    df = FeatureEngine.generate(df)

    trades = engine.detect(df, symbol, "1h")

    wins = sum(1 for t in trades if t.result == "TP")
    losses = sum(1 for t in trades if t.result == "SL")
    total = wins + losses

    win_rate = round((wins / total) * 100, 2) if total > 0 else 0

    results.append({
        "symbol": symbol,
        "trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate
    })

report = pd.DataFrame(results)

Path("reports").mkdir(exist_ok=True)
report.to_csv("reports/po3_scan_report.csv", index=False)

print()
print("REPORTE PO3")
print(report)

print()
print("Guardado en reports/po3_scan_report.csv")

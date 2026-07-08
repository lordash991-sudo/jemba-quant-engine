import csv
import json
from pathlib import Path


class PaperReport:
    def __init__(self, output_dir="reports/paper"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_summary(self, summary: dict):
        path = self.output_dir / "summary.json"

        with path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)

        return path

    def save_trades(self, trades: list):
        path = self.output_dir / "trades.csv"

        if not trades:
            with path.open("w", encoding="utf-8", newline="") as f:
                f.write("")
            return path

        fields = list(trades[0].keys())

        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(trades)

        return path

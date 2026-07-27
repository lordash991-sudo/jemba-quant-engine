from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jemba_core.lab.models import BacktestMetrics


class ReportGenerator:
    def __init__(
        self,
        output_directory: str | Path = "reports/jemba_lab",
    ) -> None:
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        results: list[BacktestMetrics],
        *,
        report_name: str = "jemba_lab_report",
    ) -> dict[str, Path]:
        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        json_path = (
            self.output_directory
            / f"{report_name}_{timestamp}.json"
        )

        csv_path = (
            self.output_directory
            / f"{report_name}_{timestamp}.csv"
        )

        payload: dict[str, Any] = {
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "result_count": len(results),
            "results": [
                result.to_dict()
                for result in results
            ],
        }

        json_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        rows = [
            result.to_dict()
            for result in results
        ]

        if rows:
            with csv_path.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=list(rows[0].keys()),
                )

                writer.writeheader()
                writer.writerows(rows)
        else:
            csv_path.write_text(
                "",
                encoding="utf-8",
            )

        return {
            "json": json_path,
            "csv": csv_path,
        }
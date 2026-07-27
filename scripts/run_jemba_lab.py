from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from jemba_core.lab import (
    AssetRanker,
    BacktestAnalyzer,
    ReportGenerator,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="JEMBA LAB V1 - Analizador de retornos históricos"
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help=(
            "CSV con columnas symbol, timeframe y return. "
            "La columna return debe usar formato decimal."
        ),
    )

    parser.add_argument(
        "--initial-capital",
        type=float,
        default=10_000.0,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/jemba_lab"),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    if not args.input.exists():
        raise FileNotFoundError(
            f"INPUT_NOT_FOUND: {args.input}"
        )

    frame = pd.read_csv(
        args.input,
        low_memory=False,
    )

    required = {
        "symbol",
        "timeframe",
        "return",
    }

    missing = required - set(frame.columns)

    if missing:
        raise ValueError(
            f"MISSING_COLUMNS: {sorted(missing)}"
        )

    analyzer = BacktestAnalyzer(
        initial_capital=args.initial_capital
    )

    results = []

    for (
        symbol,
        timeframe,
    ), group in frame.groupby(
        ["symbol", "timeframe"],
        sort=True,
    ):
        result = analyzer.analyze(
            symbol=str(symbol),
            timeframe=str(timeframe),
            trade_returns=group["return"].tolist(),
        )

        results.append(result)

    ranked = AssetRanker().rank(results)

    paths = ReportGenerator(
        args.output
    ).generate(
        ranked
    )

    print("")
    print("=" * 100)
    print("JEMBA LAB V1")
    print("=" * 100)

    for position, result in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{position:02d}. "
            f"{result.symbol:<12} "
            f"{result.timeframe:<6} "
            f"TRADES={result.total_trades:<6} "
            f"WIN={result.win_rate * 100:>7.2f}% "
            f"PF={result.profit_factor:>7.3f} "
            f"RETURN={result.total_return_pct:>9.2f}% "
            f"DD={result.max_drawdown_pct:>7.2f}% "
            f"SCORE={result.score:>7.2f}"
        )

    print("")
    print("JSON:", paths["json"])
    print("CSV:", paths["csv"])
    print("")
    print("SIN PREDICCIONES LIVE")
    print("SIN POSICIONES")
    print("SIN ORDENES REALES")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
from __future__ import annotations

import json

import pytest

from jemba_core.lab import (
    AssetRanker,
    BacktestAnalyzer,
    ReportGenerator,
)


def test_analyzer_calculates_metrics() -> None:
    analyzer = BacktestAnalyzer(
        initial_capital=10_000.0
    )

    result = analyzer.analyze(
        symbol="BTCUSDT",
        timeframe="1h",
        trade_returns=[
            0.02,
            -0.01,
            0.03,
            -0.01,
            0.01,
        ],
    )

    assert result.symbol == "BTCUSDT"
    assert result.total_trades == 5
    assert result.wins == 3
    assert result.losses == 2
    assert result.win_rate == pytest.approx(0.6)
    assert result.final_capital > 10_000.0
    assert result.profit_factor > 1.0
    assert result.max_drawdown_pct >= 0.0


def test_analyzer_rejects_invalid_capital() -> None:
    with pytest.raises(
        ValueError,
        match="INITIAL_CAPITAL",
    ):
        BacktestAnalyzer(
            initial_capital=0.0
        )


def test_analyzer_rejects_non_finite_returns() -> None:
    analyzer = BacktestAnalyzer()

    with pytest.raises(
        ValueError,
        match="FINITE",
    ):
        analyzer.analyze(
            symbol="BTCUSDT",
            timeframe="1h",
            trade_returns=[0.01, float("nan")],
        )


def test_ranker_places_best_first() -> None:
    analyzer = BacktestAnalyzer()

    strong = analyzer.analyze(
        symbol="BTCUSDT",
        timeframe="1h",
        trade_returns=[
            0.03,
            0.02,
            -0.01,
            0.02,
        ],
    )

    weak = analyzer.analyze(
        symbol="ETHUSDT",
        timeframe="1h",
        trade_returns=[
            -0.02,
            0.01,
            -0.01,
            0.005,
        ],
    )

    ranked = AssetRanker().rank(
        [weak, strong]
    )

    assert ranked[0].symbol == "BTCUSDT"


def test_report_generator_creates_files(
    tmp_path,
) -> None:
    analyzer = BacktestAnalyzer()

    result = analyzer.analyze(
        symbol="SOLUSDT",
        timeframe="1h",
        trade_returns=[
            0.01,
            -0.005,
            0.02,
        ],
    )

    paths = ReportGenerator(
        tmp_path
    ).generate(
        [result],
        report_name="test_report",
    )

    assert paths["json"].exists()
    assert paths["csv"].exists()

    payload = json.loads(
        paths["json"].read_text(
            encoding="utf-8"
        )
    )

    assert payload["result_count"] == 1
    assert payload["results"][0]["symbol"] == "SOLUSDT"
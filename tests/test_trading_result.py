import numpy as np
import pytest

from jemba_core.quant import TradingResult


def test_builds_complete_trading_result():
    result = TradingResult.from_trades(
        [100.0, -50.0, 50.0, -25.0],
        initial_equity=1000.0,
        metadata={"symbol": "BTCUSDT"},
    )

    assert result.number_of_trades == 4
    assert result.winning_trades == 2
    assert result.losing_trades == 2
    assert result.net_profit == 75.0
    assert result.final_equity == 1075.0
    assert result.profit_factor == 2.0
    assert result.win_rate == pytest.approx(0.5)
    assert result.metadata["symbol"] == "BTCUSDT"


def test_to_dict_contains_main_metrics():
    result = TradingResult.from_trades(
        [10.0, -5.0],
        initial_equity=100.0,
    )

    data = result.to_dict()

    assert data["number_of_trades"] == 2
    assert data["net_profit"] == 5.0
    assert data["final_equity"] == 105.0
    assert "max_drawdown" in data
    assert "equity_curve" in data


def test_rejects_non_finite_trades():
    with pytest.raises(
        ValueError,
        match="TRADES_MUST_BE_FINITE",
    ):
        TradingResult.from_trades([10.0, np.inf])


def test_exposes_advanced_risk_metrics():
    result = TradingResult.from_trades(
        [100.0, -40.0, 80.0, -20.0],
        initial_equity=1000.0,
    )

    assert isinstance(result.sharpe, float)
    assert isinstance(result.sortino, float)
    assert isinstance(result.calmar, float)
    assert isinstance(result.recovery_factor, float)
    assert isinstance(result.sqn, float)

    data = result.to_dict()

    assert "sharpe" in data
    assert "sortino" in data
    assert "calmar" in data
    assert "recovery_factor" in data
    assert "sqn" in data


def test_exposes_advanced_risk_metrics():
    result = TradingResult.from_trades(
        [100.0, -40.0, 80.0, -20.0],
        initial_equity=1000.0,
    )

    assert isinstance(result.sharpe, float)
    assert isinstance(result.sortino, float)
    assert isinstance(result.calmar, float)
    assert isinstance(result.recovery_factor, float)
    assert isinstance(result.sqn, float)

    data = result.to_dict()

    assert "sharpe" in data
    assert "sortino" in data
    assert "calmar" in data
    assert "recovery_factor" in data
    assert "sqn" in data

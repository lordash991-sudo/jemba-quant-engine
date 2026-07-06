from jemba_core.portfolio.portfolio_manager import PortfolioManager
from jemba_core.risk.risk_engine import RiskEngine


def test_risk_approved():
    portfolio = PortfolioManager()
    risk = RiskEngine(min_confidence=0.70)

    result = risk.validate(
        portfolio=portfolio,
        confidence=0.91,
        position_size=1,
    )

    assert result["approved"] is True
    assert result["reasons"] == []


def test_low_confidence_blocked():
    portfolio = PortfolioManager()
    risk = RiskEngine(min_confidence=0.70)

    result = risk.validate(
        portfolio=portfolio,
        confidence=0.55,
        position_size=1,
    )

    assert result["approved"] is False
    assert "LOW_CONFIDENCE" in result["reasons"]


def test_position_already_open_blocked():
    portfolio = PortfolioManager()
    risk = RiskEngine()

    result = risk.validate(
        portfolio=portfolio,
        confidence=0.90,
        position_size=1,
        has_open_position=True,
    )

    assert result["approved"] is False
    assert "POSITION_ALREADY_OPEN" in result["reasons"]

from jemba_core.portfolio.constraints.capital import CapitalConstraint
from jemba_core.portfolio.constraints.correlation import CorrelationConstraint
from jemba_core.portfolio.constraints.exposure import ExposureConstraint
from jemba_core.portfolio.models import PortfolioCandidate, PortfolioState


def test_capital_constraint_approves():
    constraint = CapitalConstraint()
    candidate = PortfolioCandidate("BTCUSDT", 95, 0.91, "LONG", allocation=1000)
    state = PortfolioState(capital=10000, used_capital=1000, open_positions=1)

    result = constraint.evaluate(candidate, state)

    assert result.approved is True


def test_capital_constraint_rejects_without_capital():
    constraint = CapitalConstraint()
    candidate = PortfolioCandidate("BTCUSDT", 95, 0.91, "LONG", allocation=1000)
    state = PortfolioState(capital=0, used_capital=0, open_positions=0)

    result = constraint.evaluate(candidate, state)

    assert result.approved is False
    assert result.reason == "NO_CAPITAL"


def test_exposure_constraint_rejects_max_positions():
    constraint = ExposureConstraint()
    candidate = PortfolioCandidate("BTCUSDT", 95, 0.91, "LONG", allocation=1000)
    state = PortfolioState(
        capital=10000,
        used_capital=1000,
        open_positions=3,
        max_positions=3,
    )

    result = constraint.evaluate(candidate, state)

    assert result.approved is False
    assert result.reason == "MAX_POSITIONS_REACHED"


def test_exposure_constraint_rejects_exposure():
    constraint = ExposureConstraint()
    candidate = PortfolioCandidate("BTCUSDT", 95, 0.91, "LONG", allocation=3000)
    state = PortfolioState(
        capital=10000,
        used_capital=2000,
        open_positions=1,
        max_total_exposure=0.35,
    )

    result = constraint.evaluate(candidate, state)

    assert result.approved is False
    assert result.reason == "MAX_EXPOSURE_EXCEEDED"


def test_correlation_constraint_rejects_high_correlation():
    constraint = CorrelationConstraint()
    candidate = PortfolioCandidate(
        "ETHUSDT",
        94,
        0.90,
        "LONG",
        allocation=1000,
        correlation=0.95,
    )
    state = PortfolioState(
        capital=10000,
        used_capital=1000,
        open_positions=1,
        max_correlation=0.80,
    )

    result = constraint.evaluate(candidate, state)

    assert result.approved is False
    assert result.reason == "CORRELATION_TOO_HIGH"

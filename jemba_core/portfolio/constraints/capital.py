from jemba_core.portfolio.constraints.base import Constraint
from jemba_core.portfolio.models import (
    ConstraintResult,
    PortfolioCandidate,
    PortfolioState,
)


class CapitalConstraint(Constraint):

    def evaluate(
        self,
        candidate: PortfolioCandidate,
        state: PortfolioState,
    ) -> ConstraintResult:
        if state.capital <= 0:
            return ConstraintResult(False, "NO_CAPITAL")

        available = state.capital - state.used_capital

        if candidate.allocation > available:
            return ConstraintResult(False, "INSUFFICIENT_CAPITAL")

        return ConstraintResult(True)

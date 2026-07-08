from jemba_core.portfolio.constraints.base import Constraint
from jemba_core.portfolio.models import (
    ConstraintResult,
    PortfolioCandidate,
    PortfolioState,
)


class CorrelationConstraint(Constraint):

    def evaluate(
        self,
        candidate: PortfolioCandidate,
        state: PortfolioState,
    ) -> ConstraintResult:
        if candidate.correlation > state.max_correlation:
            return ConstraintResult(False, "CORRELATION_TOO_HIGH")

        return ConstraintResult(True)

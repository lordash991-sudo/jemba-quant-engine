from jemba_core.portfolio.constraints.base import Constraint
from jemba_core.portfolio.models import (
    ConstraintResult,
    PortfolioCandidate,
    PortfolioState,
)


class ExposureConstraint(Constraint):
    def evaluate(
        self,
        candidate: PortfolioCandidate,
        state: PortfolioState,
    ) -> ConstraintResult:
        if state.open_positions >= state.max_positions:
            return ConstraintResult(False, "MAX_POSITIONS_REACHED")

        exposure = (state.used_capital + candidate.allocation) / state.capital

        if exposure > state.max_total_exposure:
            return ConstraintResult(False, "MAX_EXPOSURE_EXCEEDED")

        return ConstraintResult(True)

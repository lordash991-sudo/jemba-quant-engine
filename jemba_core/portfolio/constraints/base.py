from __future__ import annotations

from abc import ABC, abstractmethod

from jemba_core.portfolio.models import (
    ConstraintResult,
    PortfolioCandidate,
    PortfolioState,
)


class Constraint(ABC):
    @abstractmethod
    def evaluate(
        self,
        candidate: PortfolioCandidate,
        state: PortfolioState,
    ) -> ConstraintResult:
        pass

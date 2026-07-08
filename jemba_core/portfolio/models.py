from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioCandidate:
    symbol: str
    score: float
    confidence: float
    signal: str
    allocation: float = 0.0
    correlation: float = 0.0
    liquidity: float = 10.0
    spread: float = 0.0


@dataclass(slots=True)
class PortfolioState:
    capital: float
    used_capital: float
    open_positions: int
    max_positions: int = 3
    max_total_exposure: float = 0.35
    max_correlation: float = 0.80


@dataclass(slots=True)
class ConstraintResult:
    approved: bool
    reason: str = "APPROVED"

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioState:
    capital: float
    used_margin: float
    open_positions: int
    max_positions: int = 5


class PortfolioManager:
    def __init__(
        self,
        max_positions: int = 5,
        max_margin_pct: float = 0.80,
    ):
        self.max_positions = max_positions
        self.max_margin_pct = max_margin_pct

    def can_open(
        self,
        state: PortfolioState,
        position_size: float,
    ) -> bool:

        if state.open_positions >= self.max_positions:
            return False

        if (state.used_margin + position_size) > (state.capital * self.max_margin_pct):
            return False

        return True

    def allocate(
        self,
        state: PortfolioState,
        position_size: float,
    ) -> PortfolioState:

        if not self.can_open(state, position_size):
            return state

        return PortfolioState(
            capital=state.capital,
            used_margin=state.used_margin + position_size,
            open_positions=state.open_positions + 1,
            max_positions=state.max_positions,
        )

    def free_margin(self, state: PortfolioState) -> float:
        return state.capital - state.used_margin

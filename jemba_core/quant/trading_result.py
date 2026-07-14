from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from jemba_core.quant.drawdown import (
    average_drawdown,
    max_drawdown,
)
from jemba_core.quant.equity_curve import EquityCurve
from jemba_core.quant.expectancy import (
    average_loss,
    average_win,
    expectancy,
    loss_rate,
    win_rate,
)
from jemba_core.quant.profit_factor import (
    gross_loss,
    gross_profit,
    profit_factor,
)


@dataclass(slots=True)
class TradingResult:
    trades: NDArray[np.float64]
    initial_equity: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.trades = np.asarray(
            self.trades,
            dtype=float,
        )

        if self.trades.ndim != 1:
            raise ValueError("TRADES_MUST_BE_ONE_DIMENSIONAL")

        if not np.isfinite(self.trades).all():
            raise ValueError("TRADES_MUST_BE_FINITE")

        if not np.isfinite(self.initial_equity):
            raise ValueError("INITIAL_EQUITY_MUST_BE_FINITE")

        self.initial_equity = float(self.initial_equity)
        self.metadata = dict(self.metadata)

    @classmethod
    def from_trades(
        cls,
        trades,
        *,
        initial_equity: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> TradingResult:
        return cls(
            trades=np.asarray(
                list(trades),
                dtype=float,
            ),
            initial_equity=initial_equity,
            metadata=metadata or {},
        )

    @property
    def number_of_trades(self) -> int:
        return int(self.trades.size)

    @property
    def winning_trades(self) -> int:
        return int(np.sum(self.trades > 0))

    @property
    def losing_trades(self) -> int:
        return int(np.sum(self.trades < 0))

    @property
    def breakeven_trades(self) -> int:
        return int(np.sum(self.trades == 0))

    @property
    def net_profit(self) -> float:
        return float(np.sum(self.trades))

    @property
    def gross_profit(self) -> float:
        return gross_profit(self.trades)

    @property
    def gross_loss(self) -> float:
        return gross_loss(self.trades)

    @property
    def profit_factor(self) -> float:
        return profit_factor(self.trades)

    @property
    def win_rate(self) -> float:
        return win_rate(self.trades)

    @property
    def loss_rate(self) -> float:
        return loss_rate(self.trades)

    @property
    def average_win(self) -> float:
        return average_win(self.trades)

    @property
    def average_loss(self) -> float:
        return average_loss(self.trades)

    @property
    def expectancy(self) -> float:
        return expectancy(self.trades)

    @property
    def payoff_ratio(self) -> float:
        if self.average_loss == 0.0:
            if self.average_win > 0.0:
                return float("inf")

            return 0.0

        return float(self.average_win / self.average_loss)

    @property
    def equity_curve(self) -> NDArray[np.float64]:
        return EquityCurve(
            initial_equity=self.initial_equity,
            pnl=self.trades,
        ).to_numpy()

    @property
    def returns(self) -> NDArray[np.float64]:
        return EquityCurve(
            initial_equity=self.initial_equity,
            pnl=self.trades,
        ).returns()

    @property
    def final_equity(self) -> float:
        return float(self.equity_curve[-1])

    @property
    def max_drawdown(self) -> float:
        return max_drawdown(self.equity_curve)

    @property
    def average_drawdown(self) -> float:
        return average_drawdown(self.equity_curve)

    def to_dict(self) -> dict[str, Any]:
        return {
            "number_of_trades": self.number_of_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "breakeven_trades": self.breakeven_trades,
            "initial_equity": self.initial_equity,
            "final_equity": self.final_equity,
            "net_profit": self.net_profit,
            "gross_profit": self.gross_profit,
            "gross_loss": self.gross_loss,
            "profit_factor": self.profit_factor,
            "win_rate": self.win_rate,
            "loss_rate": self.loss_rate,
            "average_win": self.average_win,
            "average_loss": self.average_loss,
            "expectancy": self.expectancy,
            "payoff_ratio": self.payoff_ratio,
            "max_drawdown": self.max_drawdown,
            "average_drawdown": (self.average_drawdown),
            "equity_curve": (self.equity_curve.tolist()),
            "returns": self.returns.tolist(),
            "metadata": dict(self.metadata),
        }

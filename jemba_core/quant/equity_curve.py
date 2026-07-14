from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray


class EquityCurve:
    def __init__(
        self,
        *,
        initial_equity: float = 0.0,
        pnl: Iterable[float] | None = None,
    ) -> None:
        if not np.isfinite(initial_equity):
            raise ValueError("INITIAL_EQUITY_MUST_BE_FINITE")

        self.initial_equity = float(initial_equity)
        self._pnl: list[float] = []

        if pnl is not None:
            self.extend(pnl)

    def append(self, pnl: float) -> None:
        value = float(pnl)

        if not np.isfinite(value):
            raise ValueError("PNL_MUST_BE_FINITE")

        self._pnl.append(value)

    def extend(self, pnl: Iterable[float]) -> None:
        values = np.asarray(list(pnl), dtype=float)

        if values.ndim != 1:
            raise ValueError("PNL_MUST_BE_ONE_DIMENSIONAL")

        if not np.isfinite(values).all():
            raise ValueError("PNL_MUST_BE_FINITE")

        self._pnl.extend(values.tolist())

    def equity(self) -> NDArray[np.float64]:
        pnl = self.pnl()

        if pnl.size == 0:
            return np.array(
                [self.initial_equity],
                dtype=float,
            )

        cumulative = np.cumsum(pnl, dtype=float)

        return np.concatenate(
            (
                np.array(
                    [self.initial_equity],
                    dtype=float,
                ),
                self.initial_equity + cumulative,
            )
        )

    def pnl(self) -> NDArray[np.float64]:
        return np.asarray(self._pnl, dtype=float)

    def returns(self) -> NDArray[np.float64]:
        equity = self.equity()

        if equity.size < 2:
            return np.array([], dtype=float)

        previous = equity[:-1]
        changes = np.diff(equity)

        return np.divide(
            changes,
            previous,
            out=np.zeros_like(changes, dtype=float),
            where=previous != 0,
        )

    def peak(self) -> float:
        return float(np.max(self.equity()))

    def valley(self) -> float:
        return float(np.min(self.equity()))

    def final_equity(self) -> float:
        return float(self.equity()[-1])

    def to_numpy(self) -> NDArray[np.float64]:
        return self.equity().copy()

    def __len__(self) -> int:
        return len(self._pnl)

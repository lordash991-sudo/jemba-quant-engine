from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime

from jemba_core.paper_broker.models import (
    CloseReason,
    PositionSide,
    PositionSnapshot,
    PositionStatus,
)

_PRICE_REL_TOLERANCE = 1e-12
_PRICE_ABS_TOLERANCE = 1e-12


@dataclass(slots=True)
class PaperPosition:
    position_id: str
    symbol: str
    side: PositionSide

    entry_price: float
    quantity: float
    leverage: int

    stop_loss: float
    take_profit: float

    open_commission: float = 0.0

    current_price: float = field(init=False)
    status: PositionStatus = field(
        init=False,
        default=PositionStatus.OPEN,
    )

    realized_pnl: float = field(
        init=False,
        default=0.0,
    )
    close_commission: float = field(
        init=False,
        default=0.0,
    )

    opened_at: datetime = field(
        init=False,
        default_factory=lambda: datetime.now(UTC),
    )
    closed_at: datetime | None = field(
        init=False,
        default=None,
    )
    close_reason: CloseReason | None = field(
        init=False,
        default=None,
    )

    def __post_init__(self) -> None:
        self.symbol = self.symbol.strip().upper()

        if not self.symbol:
            raise ValueError("SYMBOL_CANNOT_BE_EMPTY")

        if not isinstance(self.side, PositionSide):
            raise TypeError("SIDE_MUST_BE_POSITION_SIDE")

        self.entry_price = _positive_finite(
            self.entry_price,
            "ENTRY_PRICE",
        )
        self.quantity = _positive_finite(
            self.quantity,
            "QUANTITY",
        )
        self.stop_loss = _positive_finite(
            self.stop_loss,
            "STOP_LOSS",
        )
        self.take_profit = _positive_finite(
            self.take_profit,
            "TAKE_PROFIT",
        )
        self.open_commission = _non_negative_finite(
            self.open_commission,
            "OPEN_COMMISSION",
        )

        if not isinstance(self.leverage, int):
            raise TypeError("LEVERAGE_MUST_BE_INTEGER")

        if self.leverage <= 0:
            raise ValueError("LEVERAGE_MUST_BE_POSITIVE")

        self._validate_price_structure()
        self.current_price = self.entry_price

    @property
    def notional(self) -> float:
        return float(self.entry_price * self.quantity)

    @property
    def margin_used(self) -> float:
        return float(self.notional / self.leverage)

    @property
    def unrealized_pnl(self) -> float:
        if self.status is PositionStatus.CLOSED:
            return 0.0

        return float(self._gross_pnl(self.current_price) - self.open_commission)

    def update_price(
        self,
        price: float,
    ) -> CloseReason | None:
        if self.status is PositionStatus.CLOSED:
            raise ValueError("POSITION_ALREADY_CLOSED")

        self.current_price = _positive_finite(
            price,
            "CURRENT_PRICE",
        )

        if self.side is PositionSide.LONG:
            if _price_at_or_below(
                self.current_price,
                self.stop_loss,
            ):
                return CloseReason.STOP_LOSS

            if _price_at_or_above(
                self.current_price,
                self.take_profit,
            ):
                return CloseReason.TAKE_PROFIT

        else:
            if _price_at_or_above(
                self.current_price,
                self.stop_loss,
            ):
                return CloseReason.STOP_LOSS

            if _price_at_or_below(
                self.current_price,
                self.take_profit,
            ):
                return CloseReason.TAKE_PROFIT

        return None

    def close(
        self,
        *,
        price: float,
        reason: CloseReason,
        commission: float = 0.0,
    ) -> float:
        if self.status is PositionStatus.CLOSED:
            raise ValueError("POSITION_ALREADY_CLOSED")

        close_price = _positive_finite(
            price,
            "CLOSE_PRICE",
        )
        close_commission = _non_negative_finite(
            commission,
            "CLOSE_COMMISSION",
        )

        if not isinstance(reason, CloseReason):
            raise TypeError("REASON_MUST_BE_CLOSE_REASON")

        self.current_price = close_price
        self.close_commission = close_commission

        self.realized_pnl = float(
            self._gross_pnl(close_price) - self.open_commission - close_commission
        )

        self.status = PositionStatus.CLOSED
        self.closed_at = datetime.now(UTC)
        self.close_reason = reason

        return self.realized_pnl

    def snapshot(self) -> PositionSnapshot:
        return PositionSnapshot(
            position_id=self.position_id,
            symbol=self.symbol,
            side=self.side,
            status=self.status,
            entry_price=float(self.entry_price),
            current_price=float(self.current_price),
            quantity=float(self.quantity),
            leverage=self.leverage,
            stop_loss=float(self.stop_loss),
            take_profit=float(self.take_profit),
            notional=self.notional,
            margin_used=self.margin_used,
            unrealized_pnl=self.unrealized_pnl,
            realized_pnl=float(self.realized_pnl),
            open_commission=float(self.open_commission),
            close_commission=float(self.close_commission),
            opened_at=self.opened_at,
            closed_at=self.closed_at,
            close_reason=self.close_reason,
        )

    def _gross_pnl(
        self,
        price: float,
    ) -> float:
        if self.side is PositionSide.LONG:
            return float((price - self.entry_price) * self.quantity)

        return float((self.entry_price - price) * self.quantity)

    def _validate_price_structure(self) -> None:
        if self.side is PositionSide.LONG:
            if _price_at_or_above(
                self.stop_loss,
                self.entry_price,
            ):
                raise ValueError("INVALID_LONG_STOP_LOSS")

            if _price_at_or_below(
                self.take_profit,
                self.entry_price,
            ):
                raise ValueError("INVALID_LONG_TAKE_PROFIT")

        else:
            if _price_at_or_below(
                self.stop_loss,
                self.entry_price,
            ):
                raise ValueError("INVALID_SHORT_STOP_LOSS")

            if _price_at_or_above(
                self.take_profit,
                self.entry_price,
            ):
                raise ValueError("INVALID_SHORT_TAKE_PROFIT")


def _prices_equal(
    first: float,
    second: float,
) -> bool:
    return math.isclose(
        first,
        second,
        rel_tol=_PRICE_REL_TOLERANCE,
        abs_tol=_PRICE_ABS_TOLERANCE,
    )


def _price_at_or_above(
    price: float,
    level: float,
) -> bool:
    return price > level or _prices_equal(price, level)


def _price_at_or_below(
    price: float,
    level: float,
) -> bool:
    return price < level or _prices_equal(price, level)


def _positive_finite(
    value: float,
    name: str,
) -> float:
    numeric = _finite_float(value, name)

    if numeric <= 0.0:
        raise ValueError(f"{name}_MUST_BE_POSITIVE")

    return numeric


def _non_negative_finite(
    value: float,
    name: str,
) -> float:
    numeric = _finite_float(value, name)

    if numeric < 0.0:
        raise ValueError(f"{name}_MUST_BE_NON_NEGATIVE")

    return numeric


def _finite_float(
    value: float,
    name: str,
) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name}_MUST_BE_NUMERIC") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name}_MUST_BE_FINITE")

    return numeric

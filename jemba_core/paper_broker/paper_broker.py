from __future__ import annotations

import uuid

from jemba_core.paper_broker.account import PaperAccount
from jemba_core.paper_broker.models import (
    AccountSnapshot,
    CloseReason,
    PositionSide,
    PositionSnapshot,
)
from jemba_core.paper_broker.position import PaperPosition


class PaperBroker:
    """In-memory paper broker for opening and managing positions."""

    def __init__(
        self,
        *,
        initial_balance: float = 10_000.0,
        maximum_leverage: int = 70,
        allow_hedging: bool = False,
    ) -> None:
        if not isinstance(maximum_leverage, int):
            raise TypeError("MAXIMUM_LEVERAGE_MUST_BE_INTEGER")

        if maximum_leverage <= 0:
            raise ValueError("MAXIMUM_LEVERAGE_MUST_BE_POSITIVE")

        if not isinstance(allow_hedging, bool):
            raise TypeError("ALLOW_HEDGING_MUST_BE_BOOLEAN")

        self.account = PaperAccount(initial_balance)
        self.maximum_leverage = maximum_leverage
        self.allow_hedging = allow_hedging

        self._open_positions: dict[str, PaperPosition] = {}
        self._closed_positions: list[PaperPosition] = []

    def open_position(
        self,
        *,
        symbol: str,
        side: PositionSide,
        entry_price: float,
        quantity: float,
        leverage: int,
        stop_loss: float,
        take_profit: float,
        commission: float = 0.0,
    ) -> PositionSnapshot:
        normalized_symbol = symbol.strip().upper()

        if leverage > self.maximum_leverage:
            raise ValueError("LEVERAGE_LIMIT_EXCEEDED")

        self._validate_duplicate_position(
            normalized_symbol,
            side,
        )

        position = PaperPosition(
            position_id=uuid.uuid4().hex,
            symbol=normalized_symbol,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            leverage=leverage,
            stop_loss=stop_loss,
            take_profit=take_profit,
            open_commission=commission,
        )

        current_positions = tuple(self._open_positions.values())

        self.account.reserve_margin(
            position,
            current_positions,
        )

        self._open_positions[position.position_id] = position

        return position.snapshot()

    def update_market_price(
        self,
        *,
        symbol: str,
        price: float,
        close_commission_rate: float = 0.0,
    ) -> tuple[PositionSnapshot, ...]:
        normalized_symbol = symbol.strip().upper()

        affected = tuple(
            position
            for position in self._open_positions.values()
            if position.symbol == normalized_symbol
        )

        updated: list[PositionSnapshot] = []

        for position in affected:
            close_reason = position.update_price(price)

            if close_reason is not None:
                commission = price * position.quantity * close_commission_rate

                self._close_position_object(
                    position,
                    price=price,
                    reason=close_reason,
                    commission=commission,
                )

            updated.append(position.snapshot())

        return tuple(updated)

    def close_position(
        self,
        position_id: str,
        *,
        price: float,
        commission: float = 0.0,
    ) -> PositionSnapshot:
        position = self._get_open_position(position_id)

        self._close_position_object(
            position,
            price=price,
            reason=CloseReason.MANUAL,
            commission=commission,
        )

        return position.snapshot()

    def get_position(
        self,
        position_id: str,
    ) -> PositionSnapshot:
        if position_id in self._open_positions:
            return self._open_positions[position_id].snapshot()

        for position in self._closed_positions:
            if position.position_id == position_id:
                return position.snapshot()

        raise KeyError("POSITION_NOT_FOUND")

    def open_positions(
        self,
    ) -> tuple[PositionSnapshot, ...]:
        return tuple(position.snapshot() for position in self._open_positions.values())

    def closed_positions(
        self,
    ) -> tuple[PositionSnapshot, ...]:
        return tuple(position.snapshot() for position in self._closed_positions)

    def account_snapshot(self) -> AccountSnapshot:
        return self.account.snapshot(
            tuple(self._open_positions.values()),
            tuple(self._closed_positions),
        )

    def _close_position_object(
        self,
        position: PaperPosition,
        *,
        price: float,
        reason: CloseReason,
        commission: float,
    ) -> None:
        position.close(
            price=price,
            reason=reason,
            commission=commission,
        )

        self.account.apply_closed_position(position)

        del self._open_positions[position.position_id]
        self._closed_positions.append(position)

    def _get_open_position(
        self,
        position_id: str,
    ) -> PaperPosition:
        try:
            return self._open_positions[position_id]
        except KeyError as exc:
            raise KeyError("OPEN_POSITION_NOT_FOUND") from exc

    def _validate_duplicate_position(
        self,
        symbol: str,
        side: PositionSide,
    ) -> None:
        for position in self._open_positions.values():
            if position.symbol != symbol:
                continue

            if not self.allow_hedging:
                raise ValueError("DUPLICATE_SYMBOL_POSITION")

            if position.side is side:
                raise ValueError("DUPLICATE_DIRECTION_POSITION")

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

from jemba_core.paper_broker.models import (
    CloseReason,
    PositionSide,
    PositionSnapshot,
)
from jemba_core.paper_broker.paper_broker import PaperBroker
from jemba_core.paper_broker.position import PaperPosition
from jemba_core.paper_broker.trade_management import (
    ManagedPositionState,
    TradeManagementConfig,
    TradeManagementEvent,
    TradeManagementEventType,
)


class ManagedPaperBroker(PaperBroker):
    """
    Paper Broker with Break Even, partial exits, trailing stops,
    and time-based exits.
    """

    def __init__(
        self,
        *,
        initial_balance: float = 10_000.0,
        maximum_leverage: int = 70,
        allow_hedging: bool = False,
        management_config: TradeManagementConfig | None = None,
    ) -> None:
        super().__init__(
            initial_balance=initial_balance,
            maximum_leverage=maximum_leverage,
            allow_hedging=allow_hedging,
        )

        self.management_config = management_config or TradeManagementConfig()

        self._management_states: dict[
            str,
            ManagedPositionState,
        ] = {}

        self._management_events: list[TradeManagementEvent] = []

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
        snapshot = super().open_position(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            leverage=leverage,
            stop_loss=stop_loss,
            take_profit=take_profit,
            commission=commission,
        )

        risk_distance = abs(snapshot.entry_price - snapshot.stop_loss)

        self._management_states[snapshot.position_id] = ManagedPositionState(
            position_id=snapshot.position_id,
            initial_quantity=snapshot.quantity,
            initial_stop_loss=snapshot.stop_loss,
            risk_distance=risk_distance,
            highest_price=snapshot.entry_price,
            lowest_price=snapshot.entry_price,
        )

        return snapshot

    def update_managed_price(
        self,
        *,
        symbol: str,
        price: float,
        now: datetime | None = None,
        close_commission_rate: float = 0.0,
    ) -> tuple[TradeManagementEvent, ...]:
        normalized_symbol = symbol.strip().upper()
        current_price = _positive_finite(
            price,
            "CURRENT_PRICE",
        )

        timestamp = now or datetime.now(UTC)

        if timestamp.tzinfo is None:
            raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")

        commission_rate = _non_negative_finite(
            close_commission_rate,
            "CLOSE_COMMISSION_RATE",
        )

        matching_positions = tuple(
            position
            for position in self._open_positions.values()
            if position.symbol == normalized_symbol
        )

        generated_events: list[TradeManagementEvent] = []

        for position in matching_positions:
            state = self._management_states[position.position_id]

            time_stop_event = self._apply_time_stop(
                position=position,
                state=state,
                price=current_price,
                timestamp=timestamp,
                commission_rate=commission_rate,
            )

            if time_stop_event is not None:
                generated_events.append(time_stop_event)
                continue

            state.highest_price = max(
                state.highest_price,
                current_price,
            )
            state.lowest_price = min(
                state.lowest_price,
                current_price,
            )

            current_rr = self._current_rr(
                position,
                state,
                current_price,
            )

            break_even_event = self._apply_break_even(
                position=position,
                state=state,
                current_rr=current_rr,
                price=current_price,
                timestamp=timestamp,
            )

            if break_even_event is not None:
                generated_events.append(break_even_event)

            partial_event = self._apply_partial_take_profit(
                position=position,
                state=state,
                current_rr=current_rr,
                price=current_price,
                timestamp=timestamp,
                commission_rate=commission_rate,
            )

            if partial_event is not None:
                generated_events.append(partial_event)

            trailing_event = self._apply_trailing_stop(
                position=position,
                state=state,
                current_rr=current_rr,
                price=current_price,
                timestamp=timestamp,
            )

            if trailing_event is not None:
                generated_events.append(trailing_event)

            close_reason = position.update_price(current_price)

            if close_reason is not None:
                close_commission = current_price * position.quantity * commission_rate

                self._close_position_object(
                    position,
                    price=current_price,
                    reason=close_reason,
                    commission=close_commission,
                )

                event_type = (
                    TradeManagementEventType.STOP_LOSS
                    if close_reason is CloseReason.STOP_LOSS
                    else TradeManagementEventType.TAKE_PROFIT
                )

                close_event = TradeManagementEvent(
                    event_type=event_type,
                    position_id=position.position_id,
                    symbol=position.symbol,
                    price=current_price,
                    quantity=position.quantity,
                    realized_pnl=position.realized_pnl,
                    timestamp=timestamp,
                )

                generated_events.append(close_event)
                self._register_event(close_event)

                self._management_states.pop(
                    position.position_id,
                    None,
                )

        return tuple(generated_events)

    def close_position(
        self,
        position_id: str,
        *,
        price: float,
        commission: float = 0.0,
    ) -> PositionSnapshot:
        snapshot = super().close_position(
            position_id,
            price=price,
            commission=commission,
        )

        self._management_states.pop(
            position_id,
            None,
        )

        return snapshot

    def management_events(
        self,
    ) -> tuple[TradeManagementEvent, ...]:
        return tuple(self._management_events)

    def management_state(
        self,
        position_id: str,
    ) -> ManagedPositionState:
        try:
            return self._management_states[position_id]
        except KeyError as exc:
            raise KeyError("MANAGEMENT_STATE_NOT_FOUND") from exc

    def _apply_break_even(
        self,
        *,
        position: PaperPosition,
        state: ManagedPositionState,
        current_rr: float,
        price: float,
        timestamp: datetime,
    ) -> TradeManagementEvent | None:
        config = self.management_config

        if state.break_even_applied:
            return None

        if current_rr < config.break_even_trigger_rr:
            return None

        offset = state.risk_distance * config.break_even_offset_rr

        if position.side is PositionSide.LONG:
            new_stop_loss = position.entry_price + offset

            if new_stop_loss <= position.stop_loss:
                state.break_even_applied = True
                return None
        else:
            new_stop_loss = position.entry_price - offset

            if new_stop_loss >= position.stop_loss:
                state.break_even_applied = True
                return None

        position.stop_loss = float(new_stop_loss)
        state.break_even_applied = True

        event = TradeManagementEvent(
            event_type=TradeManagementEventType.BREAK_EVEN,
            position_id=position.position_id,
            symbol=position.symbol,
            price=price,
            quantity=position.quantity,
            new_stop_loss=float(new_stop_loss),
            timestamp=timestamp,
        )

        self._register_event(event)
        return event

    def _apply_partial_take_profit(
        self,
        *,
        position: PaperPosition,
        state: ManagedPositionState,
        current_rr: float,
        price: float,
        timestamp: datetime,
        commission_rate: float,
    ) -> TradeManagementEvent | None:
        config = self.management_config

        if state.partial_take_profit_applied:
            return None

        if current_rr < config.partial_take_profit_trigger_rr:
            return None

        close_quantity = position.quantity * config.partial_take_profit_fraction

        if close_quantity <= 0.0:
            return None

        remaining_quantity = position.quantity - close_quantity

        allocated_open_commission = (
            position.open_commission * config.partial_take_profit_fraction
        )

        close_commission = price * close_quantity * commission_rate

        if position.side is PositionSide.LONG:
            gross_pnl = (price - position.entry_price) * close_quantity
        else:
            gross_pnl = (position.entry_price - price) * close_quantity

        realized_pnl = gross_pnl - allocated_open_commission - close_commission

        position.quantity = float(remaining_quantity)

        position.open_commission = float(
            position.open_commission - allocated_open_commission
        )

        self.account.realized_pnl += realized_pnl
        self.account.cash_balance += realized_pnl

        state.partial_take_profit_applied = True

        event = TradeManagementEvent(
            event_type=(TradeManagementEventType.PARTIAL_TAKE_PROFIT),
            position_id=position.position_id,
            symbol=position.symbol,
            price=price,
            quantity=float(close_quantity),
            realized_pnl=float(realized_pnl),
            timestamp=timestamp,
        )

        self._register_event(event)
        return event

    def _apply_trailing_stop(
        self,
        *,
        position: PaperPosition,
        state: ManagedPositionState,
        current_rr: float,
        price: float,
        timestamp: datetime,
    ) -> TradeManagementEvent | None:
        config = self.management_config

        if current_rr < config.trailing_stop_trigger_rr:
            return None

        trailing_distance = state.risk_distance * config.trailing_stop_distance_rr

        if position.side is PositionSide.LONG:
            candidate_stop = state.highest_price - trailing_distance

            if candidate_stop <= position.stop_loss:
                return None
        else:
            candidate_stop = state.lowest_price + trailing_distance

            if candidate_stop >= position.stop_loss:
                return None

        position.stop_loss = float(candidate_stop)
        state.trailing_stop_active = True

        event = TradeManagementEvent(
            event_type=TradeManagementEventType.TRAILING_STOP,
            position_id=position.position_id,
            symbol=position.symbol,
            price=price,
            quantity=position.quantity,
            new_stop_loss=float(candidate_stop),
            timestamp=timestamp,
        )

        self._register_event(event)
        return event

    def _apply_time_stop(
        self,
        *,
        position: PaperPosition,
        state: ManagedPositionState,
        price: float,
        timestamp: datetime,
        commission_rate: float,
    ) -> TradeManagementEvent | None:
        maximum_minutes = self.management_config.maximum_hold_minutes

        if maximum_minutes is None:
            return None

        maximum_duration = timedelta(minutes=maximum_minutes)

        if timestamp - position.opened_at < maximum_duration:
            return None

        close_commission = price * position.quantity * commission_rate

        quantity = position.quantity

        self._close_position_object(
            position,
            price=price,
            reason=CloseReason.MANUAL,
            commission=close_commission,
        )

        event = TradeManagementEvent(
            event_type=TradeManagementEventType.TIME_STOP,
            position_id=position.position_id,
            symbol=position.symbol,
            price=price,
            quantity=quantity,
            realized_pnl=position.realized_pnl,
            timestamp=timestamp,
        )

        self._register_event(event)

        self._management_states.pop(
            state.position_id,
            None,
        )

        return event

    @staticmethod
    def _current_rr(
        position: PaperPosition,
        state: ManagedPositionState,
        current_price: float,
    ) -> float:
        if state.risk_distance <= 0.0:
            return 0.0

        if position.side is PositionSide.LONG:
            reward_distance = current_price - position.entry_price
        else:
            reward_distance = position.entry_price - current_price

        return float(reward_distance / state.risk_distance)

    def _register_event(
        self,
        event: TradeManagementEvent,
    ) -> None:
        self._management_events.append(event)


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

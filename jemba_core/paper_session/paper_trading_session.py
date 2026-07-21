from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from jemba_core.paper_broker import (
    ManagedPaperBroker,
    PositionSnapshot,
    TradeManagementConfig,
)
from jemba_core.paper_session.models import (
    MarketPriceUpdate,
    PaperSessionEvent,
    PaperSessionEventType,
    PaperSessionSnapshot,
    PaperSessionStatus,
    PaperSessionUpdateResult,
    PaperTradeRequest,
)


class PaperTradingSession:
    """
    Coordinate a complete paper-trading session.

    The session:
    - receives trade requests,
    - opens paper positions,
    - processes market prices,
    - activates trade management,
    - records auditable events,
    - exposes account and position snapshots.
    """

    def __init__(
        self,
        *,
        initial_balance: float = 10_000.0,
        maximum_leverage: int = 70,
        allow_hedging: bool = False,
        management_config: TradeManagementConfig | None = None,
        session_id: str | None = None,
    ) -> None:
        self.session_id = (
            session_id.strip() if session_id is not None else uuid.uuid4().hex
        )

        if not self.session_id:
            raise ValueError("SESSION_ID_CANNOT_BE_EMPTY")

        self.broker = ManagedPaperBroker(
            initial_balance=initial_balance,
            maximum_leverage=maximum_leverage,
            allow_hedging=allow_hedging,
            management_config=management_config,
        )

        self.status = PaperSessionStatus.CREATED
        self.started_at: datetime | None = None
        self.stopped_at: datetime | None = None

        self.kill_switch = False

        self._events: list[PaperSessionEvent] = []
        self._processed_price_updates = 0
        self._opened_positions = 0
        self._rejected_positions = 0

    def start(
        self,
        *,
        timestamp: datetime | None = None,
    ) -> PaperSessionSnapshot:
        if self.status is PaperSessionStatus.RUNNING:
            raise ValueError("SESSION_ALREADY_RUNNING")

        if self.status in (
            PaperSessionStatus.STOPPED,
            PaperSessionStatus.COMPLETED,
        ):
            raise ValueError("SESSION_CANNOT_BE_RESTARTED")

        now = _timezone_aware_timestamp(timestamp)

        self.status = PaperSessionStatus.RUNNING
        self.started_at = now

        self._register_event(
            PaperSessionEvent(
                event_type=(PaperSessionEventType.SESSION_STARTED),
                timestamp=now,
                message="PAPER_SESSION_STARTED",
            )
        )

        return self.snapshot()

    def stop(
        self,
        *,
        timestamp: datetime | None = None,
        completed: bool = False,
    ) -> PaperSessionSnapshot:
        self._require_running()

        now = _timezone_aware_timestamp(timestamp)

        self.status = (
            PaperSessionStatus.COMPLETED if completed else PaperSessionStatus.STOPPED
        )
        self.stopped_at = now

        self._register_event(
            PaperSessionEvent(
                event_type=(PaperSessionEventType.SESSION_STOPPED),
                timestamp=now,
                message=(
                    "PAPER_SESSION_COMPLETED" if completed else "PAPER_SESSION_STOPPED"
                ),
            )
        )

        return self.snapshot()

    def activate_kill_switch(
        self,
        *,
        timestamp: datetime | None = None,
        message: str = "MANUAL_KILL_SWITCH",
    ) -> PaperSessionSnapshot:
        now = _timezone_aware_timestamp(timestamp)

        self.kill_switch = True

        self._register_event(
            PaperSessionEvent(
                event_type=(PaperSessionEventType.KILL_SWITCH_ACTIVATED),
                timestamp=now,
                message=message,
            )
        )

        return self.snapshot()

    def open_trade(
        self,
        request: PaperTradeRequest,
        *,
        timestamp: datetime | None = None,
    ) -> PositionSnapshot | None:
        self._require_running()

        if not isinstance(request, PaperTradeRequest):
            raise TypeError("REQUEST_MUST_BE_PAPER_TRADE_REQUEST")

        now = _timezone_aware_timestamp(timestamp)

        if self.kill_switch:
            self._rejected_positions += 1

            self._register_event(
                PaperSessionEvent(
                    event_type=(PaperSessionEventType.POSITION_REJECTED),
                    timestamp=now,
                    symbol=request.symbol,
                    message="KILL_SWITCH_ACTIVE",
                )
            )

            return None

        try:
            position = self.broker.open_position(
                symbol=request.symbol,
                side=request.side,
                entry_price=request.entry_price,
                quantity=request.quantity,
                leverage=request.leverage,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
                commission=request.commission,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            self._rejected_positions += 1

            self._register_event(
                PaperSessionEvent(
                    event_type=(PaperSessionEventType.POSITION_REJECTED),
                    timestamp=now,
                    symbol=request.symbol,
                    message=str(exc),
                )
            )

            return None

        self._opened_positions += 1

        self._register_event(
            PaperSessionEvent(
                event_type=(PaperSessionEventType.POSITION_OPENED),
                timestamp=now,
                symbol=position.symbol,
                position_id=position.position_id,
                message="POSITION_OPENED",
            )
        )

        return position

    def process_price(
        self,
        update: MarketPriceUpdate,
        *,
        close_commission_rate: float = 0.0,
    ) -> PaperSessionUpdateResult:
        self._require_running()

        if not isinstance(update, MarketPriceUpdate):
            raise TypeError("UPDATE_MUST_BE_MARKET_PRICE_UPDATE")

        open_before = {
            position.position_id for position in self.broker.open_positions()
        }

        management_events = self.broker.update_managed_price(
            symbol=update.symbol,
            price=update.price,
            now=update.timestamp,
            close_commission_rate=(close_commission_rate),
        )

        open_after = {position.position_id for position in self.broker.open_positions()}

        closed_ids = open_before - open_after

        self._processed_price_updates += 1

        self._register_event(
            PaperSessionEvent(
                event_type=(PaperSessionEventType.PRICE_UPDATED),
                timestamp=update.timestamp,
                symbol=update.symbol,
                message=f"PRICE={update.price}",
            )
        )

        for position_id in closed_ids:
            snapshot = self.broker.get_position(position_id)

            self._register_event(
                PaperSessionEvent(
                    event_type=(PaperSessionEventType.POSITION_CLOSED),
                    timestamp=update.timestamp,
                    symbol=snapshot.symbol,
                    position_id=position_id,
                    message=(
                        snapshot.close_reason.value
                        if snapshot.close_reason is not None
                        else "POSITION_CLOSED"
                    ),
                )
            )

        return PaperSessionUpdateResult(
            price_update=update,
            management_events=management_events,
            session_snapshot=self.snapshot(),
        )

    def process_prices(
        self,
        updates: Sequence[MarketPriceUpdate],
        *,
        close_commission_rate: float = 0.0,
    ) -> tuple[PaperSessionUpdateResult, ...]:
        self._require_running()

        if isinstance(updates, (str, bytes)):
            raise TypeError("UPDATES_MUST_BE_SEQUENCE")

        try:
            values = tuple(updates)
        except TypeError as exc:
            raise TypeError("UPDATES_MUST_BE_SEQUENCE") from exc

        if not values:
            raise ValueError("UPDATES_CANNOT_BE_EMPTY")

        ordered = tuple(
            sorted(
                values,
                key=lambda item: item.timestamp,
            )
        )

        return tuple(
            self.process_price(
                update,
                close_commission_rate=(close_commission_rate),
            )
            for update in ordered
        )

    def close_position(
        self,
        position_id: str,
        *,
        price: float,
        commission: float = 0.0,
        timestamp: datetime | None = None,
    ) -> PositionSnapshot:
        self._require_running()

        now = _timezone_aware_timestamp(timestamp)

        position = self.broker.close_position(
            position_id,
            price=price,
            commission=commission,
        )

        self._register_event(
            PaperSessionEvent(
                event_type=(PaperSessionEventType.POSITION_CLOSED),
                timestamp=now,
                symbol=position.symbol,
                position_id=position.position_id,
                message="MANUAL",
            )
        )

        return position

    def snapshot(self) -> PaperSessionSnapshot:
        return PaperSessionSnapshot(
            session_id=self.session_id,
            status=self.status,
            started_at=self.started_at,
            stopped_at=self.stopped_at,
            processed_price_updates=(self._processed_price_updates),
            opened_positions=self._opened_positions,
            rejected_positions=self._rejected_positions,
            management_events=len(self.broker.management_events()),
            account=self.broker.account_snapshot(),
            open_positions=self.broker.open_positions(),
            closed_positions=(self.broker.closed_positions()),
            events=tuple(self._events),
        )

    def _require_running(self) -> None:
        if self.status is not PaperSessionStatus.RUNNING:
            raise ValueError("SESSION_MUST_BE_RUNNING")

    def _register_event(
        self,
        event: PaperSessionEvent,
    ) -> None:
        self._events.append(event)


def _timezone_aware_timestamp(
    value: datetime | None,
) -> datetime:
    timestamp = value or datetime.now(UTC)

    if timestamp.tzinfo is None:
        raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")

    return timestamp

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from jemba_core.market_replay import (
    Candle,
    CSVReplayEngine,
    ReplayEvent,
)
from jemba_core.paper_session import (
    MarketPriceUpdate,
    PaperTradeRequest,
    PaperTradingSession,
)
from jemba_core.replay_runner.models import (
    ReplayRunnerResult,
    ReplayRunnerStatistics,
    ReplayRunnerStatus,
    ReplaySignalAction,
    ReplaySignalRecord,
    ReplayStrategyContext,
    ReplayTradeSignal,
)
from jemba_core.replay_runner.strategy import ReplayStrategy

SignalFilter = Callable[
    [ReplayTradeSignal, ReplayStrategyContext],
    tuple[bool, str | None],
]


class ReplayStrategyRunner:
    """
    Connect CSVReplayEngine, ReplayStrategy and PaperTradingSession.

    Every candle follows this order:

    1. Update existing paper positions.
    2. Build strategy context.
    3. Request a signal.
    4. Validate optional signal filter.
    5. Open a paper trade when approved.
    """

    def __init__(
        self,
        *,
        replay_engine: CSVReplayEngine,
        session: PaperTradingSession,
        strategy: ReplayStrategy,
        minimum_confidence: float = 70.0,
        close_commission_rate: float = 0.0,
        signal_filter: SignalFilter | None = None,
    ) -> None:
        if not isinstance(
            replay_engine,
            CSVReplayEngine,
        ):
            raise TypeError("REPLAY_ENGINE_MUST_BE_CSV_REPLAY_ENGINE")

        if not isinstance(
            session,
            PaperTradingSession,
        ):
            raise TypeError("SESSION_MUST_BE_PAPER_TRADING_SESSION")

        if not isinstance(strategy, ReplayStrategy):
            raise TypeError("STRATEGY_MUST_BE_REPLAY_STRATEGY")

        if not 0.0 <= minimum_confidence <= 100.0:
            raise ValueError("MINIMUM_CONFIDENCE_MUST_BE_BETWEEN_0_AND_100")

        if close_commission_rate < 0.0:
            raise ValueError("CLOSE_COMMISSION_RATE_MUST_BE_NON_NEGATIVE")

        if signal_filter is not None and not callable(signal_filter):
            raise TypeError("SIGNAL_FILTER_MUST_BE_CALLABLE_OR_NONE")

        self.replay_engine = replay_engine
        self.session = session
        self.strategy = strategy

        self.minimum_confidence = float(minimum_confidence)
        self.close_commission_rate = float(close_commission_rate)
        self.signal_filter = signal_filter

        self.status = ReplayRunnerStatus.CREATED

        self._signals: list[ReplaySignalRecord] = []

        self._symbol_indices: dict[
            str,
            int,
        ] = defaultdict(int)

        self._previous_candles: dict[str, Candle] = {}
        self._processed_candles = 0
        self._generated_signals = 0
        self._approved_signals = 0
        self._rejected_signals = 0
        self._hold_events = 0

    def run(self) -> ReplayRunnerResult:
        if self.status is ReplayRunnerStatus.RUNNING:
            raise ValueError("RUNNER_ALREADY_RUNNING")

        self.status = ReplayRunnerStatus.RUNNING

        if self.session.status.value == "CREATED":
            self.session.start()

        self.replay_engine.subscribe(self._on_replay_event)

        try:
            self.replay_engine.play()
        finally:
            self.replay_engine.unsubscribe(self._on_replay_event)

        self.status = ReplayRunnerStatus.COMPLETED

        return self.result()

    def stop(self) -> ReplayRunnerResult:
        self.replay_engine.stop()
        self.status = ReplayRunnerStatus.STOPPED

        return self.result()

    def result(self) -> ReplayRunnerResult:
        return ReplayRunnerResult(
            status=self.status,
            statistics=self.statistics(),
            signals=tuple(self._signals),
        )

    def statistics(self) -> ReplayRunnerStatistics:
        snapshot = self.session.snapshot()
        account = snapshot.account

        total_return_percent = (account.equity / account.initial_balance - 1.0) * 100.0

        symbols = tuple(
            sorted(
                {record.symbol for record in self._signals}
                | {position.symbol for position in snapshot.open_positions}
                | {position.symbol for position in snapshot.closed_positions}
            )
        )

        return ReplayRunnerStatistics(
            processed_candles=self._processed_candles,
            generated_signals=self._generated_signals,
            approved_signals=self._approved_signals,
            rejected_signals=self._rejected_signals,
            hold_events=self._hold_events,
            opened_positions=snapshot.opened_positions,
            closed_positions=len(snapshot.closed_positions),
            open_positions=len(snapshot.open_positions),
            initial_balance=(account.initial_balance),
            final_cash_balance=(account.cash_balance),
            final_equity=account.equity,
            realized_pnl=account.realized_pnl,
            unrealized_pnl=account.unrealized_pnl,
            total_return_percent=float(total_return_percent),
            symbols=symbols,
        )

    def _on_replay_event(
        self,
        event: ReplayEvent,
    ) -> None:
        candle = event.candle
        symbol = candle.symbol

        self.session.process_price(
            MarketPriceUpdate(
                symbol=symbol,
                price=candle.close,
                timestamp=candle.timestamp,
            ),
            close_commission_rate=(self.close_commission_rate),
        )

        symbol_index = self._symbol_indices[symbol]

        has_open_position = any(
            position.symbol == symbol
            for position in self.session.snapshot().open_positions
        )

        account = self.session.snapshot().account

        context = ReplayStrategyContext(
            candle=candle,
            candle_index=event.index,
            symbol_candle_index=symbol_index,
            has_open_position=has_open_position,
            account_equity=account.equity,
            free_margin=account.free_margin,
            previous_candle=(self._previous_candles.get(symbol)),
        )

        signal = self.strategy.on_candle(context)

        if signal is None:
            self._hold_events += 1

            self._signals.append(
                ReplaySignalRecord(
                    candle_index=event.index,
                    timestamp=candle.timestamp,
                    symbol=symbol,
                    action=ReplaySignalAction.HOLD,
                    confidence=None,
                    approved=False,
                    position_id=None,
                    reason="NO_SIGNAL",
                )
            )
        else:
            self._process_signal(
                signal,
                context,
            )

        self._previous_candles[symbol] = candle
        self._symbol_indices[symbol] += 1
        self._processed_candles += 1

    def _process_signal(
        self,
        signal: ReplayTradeSignal,
        context: ReplayStrategyContext,
    ) -> None:
        self._generated_signals += 1

        if signal.symbol != context.candle.symbol:
            self._reject_signal(
                signal=signal,
                context=context,
                reason="SIGNAL_SYMBOL_MISMATCH",
            )
            return

        if signal.confidence < self.minimum_confidence:
            self._reject_signal(
                signal=signal,
                context=context,
                reason="CONFIDENCE_TOO_LOW",
            )
            return

        if context.has_open_position:
            self._reject_signal(
                signal=signal,
                context=context,
                reason="POSITION_ALREADY_OPEN",
            )
            return

        if self.signal_filter is not None:
            approved, reason = self.signal_filter(
                signal,
                context,
            )

            if not approved:
                self._reject_signal(
                    signal=signal,
                    context=context,
                    reason=(reason or "SIGNAL_FILTER_REJECTED"),
                )
                return

        position = self.session.open_trade(
            PaperTradeRequest(
                symbol=signal.symbol,
                side=signal.side,
                entry_price=context.candle.close,
                quantity=signal.quantity,
                leverage=signal.leverage,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                commission=signal.commission,
            ),
            timestamp=context.candle.timestamp,
        )

        if position is None:
            self._reject_signal(
                signal=signal,
                context=context,
                reason="SESSION_REJECTED_SIGNAL",
            )
            return

        self._approved_signals += 1

        self._signals.append(
            ReplaySignalRecord(
                candle_index=context.candle_index,
                timestamp=context.candle.timestamp,
                symbol=signal.symbol,
                action=ReplaySignalAction.OPEN,
                confidence=signal.confidence,
                approved=True,
                position_id=position.position_id,
                reason=signal.reason,
            )
        )

    def _reject_signal(
        self,
        *,
        signal: ReplayTradeSignal,
        context: ReplayStrategyContext,
        reason: str,
    ) -> None:
        self._rejected_signals += 1

        self._signals.append(
            ReplaySignalRecord(
                candle_index=context.candle_index,
                timestamp=context.candle.timestamp,
                symbol=context.candle.symbol,
                action=ReplaySignalAction.OPEN,
                confidence=signal.confidence,
                approved=False,
                position_id=None,
                reason=reason,
            )
        )

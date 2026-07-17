from jemba_core.trade_manager.orchestrator import (
    TradeAction,
    TradeDecision,
    TradeManager,
)


def test_hold_when_no_rule_is_triggered():
    manager = TradeManager()

    decision = manager.decide()

    assert decision == TradeDecision(
        action=TradeAction.HOLD,
    )


def test_atr_stop_has_highest_priority():
    manager = TradeManager()

    decision = manager.decide(
        atr_stop=True,
        time_stop=True,
        partial_tp=True,
        break_even=True,
        trailing=True,
    )

    assert decision.action is TradeAction.CLOSE
    assert decision.reason == "ATR_STOP"


def test_time_stop_has_priority_over_management_actions():
    manager = TradeManager()

    decision = manager.decide(
        time_stop=True,
        partial_tp=True,
        break_even=True,
        trailing=True,
    )

    assert decision.action is TradeAction.CLOSE
    assert decision.reason == "TIME_STOP"


def test_partial_take_profit_has_priority_over_stop_updates():
    manager = TradeManager()

    decision = manager.decide(
        partial_tp=True,
        break_even=True,
        trailing=True,
    )

    assert decision.action is TradeAction.PARTIAL
    assert decision.reason == "PARTIAL_TP"


def test_break_even_has_priority_over_trailing():
    manager = TradeManager()

    decision = manager.decide(
        break_even=True,
        trailing=True,
    )

    assert decision.action is TradeAction.BREAK_EVEN
    assert decision.reason == "BREAK_EVEN"


def test_trailing_is_selected_when_it_is_the_only_trigger():
    manager = TradeManager()

    decision = manager.decide(
        trailing=True,
    )

    assert decision.action is TradeAction.TRAIL
    assert decision.reason == "TRAILING"


def test_trade_action_is_string_enum():
    assert TradeAction.CLOSE.value == "close"
    assert str(TradeAction.CLOSE) == "close"

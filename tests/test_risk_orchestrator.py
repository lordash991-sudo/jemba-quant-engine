import pytest

from jemba_core.risk_engine.risk_orchestrator import (
    RiskAction,
    RiskDecision,
    RiskLimits,
    RiskManager,
)


def valid_inputs():
    return {
        "risk_fraction": 0.01,
        "daily_loss_fraction": 0.01,
        "drawdown_fraction": 0.04,
        "open_positions": 2,
        "total_exposure_fraction": 0.40,
        "probability_of_ruin": 0.02,
    }


def test_allows_trade_inside_limits():
    manager = RiskManager()

    decision = manager.evaluate(**valid_inputs())

    assert decision == RiskDecision(
        action=RiskAction.ALLOW,
    )
    assert decision.allowed is True


def test_kill_switch_has_highest_priority():
    manager = RiskManager()

    decision = manager.evaluate(
        **valid_inputs(),
        kill_switch=True,
    )

    assert decision.action is RiskAction.KILL_SWITCH
    assert decision.reason == "KILL_SWITCH_ACTIVE"
    assert decision.allowed is False


def test_blocks_daily_loss_limit():
    manager = RiskManager()
    values = valid_inputs()
    values["daily_loss_fraction"] = 0.03

    decision = manager.evaluate(**values)

    assert decision.action is RiskAction.BLOCK
    assert decision.reason == "DAILY_LOSS_LIMIT"


def test_blocks_max_drawdown():
    manager = RiskManager()
    values = valid_inputs()
    values["drawdown_fraction"] = 0.10

    decision = manager.evaluate(**values)

    assert decision.reason == "MAX_DRAWDOWN_LIMIT"


def test_blocks_probability_of_ruin():
    manager = RiskManager()
    values = valid_inputs()
    values["probability_of_ruin"] = 0.06

    decision = manager.evaluate(**values)

    assert decision.reason == "PROBABILITY_OF_RUIN_LIMIT"


def test_blocks_max_open_positions():
    manager = RiskManager()
    values = valid_inputs()
    values["open_positions"] = 5

    decision = manager.evaluate(**values)

    assert decision.reason == "MAX_OPEN_POSITIONS"


def test_blocks_total_exposure():
    manager = RiskManager()
    values = valid_inputs()
    values["total_exposure_fraction"] = 1.0

    decision = manager.evaluate(**values)

    assert decision.reason == "TOTAL_EXPOSURE_LIMIT"


def test_blocks_risk_per_trade():
    manager = RiskManager()
    values = valid_inputs()
    values["risk_fraction"] = 0.02

    decision = manager.evaluate(**values)

    assert decision.reason == "RISK_PER_TRADE_LIMIT"


def test_supports_custom_limits():
    limits = RiskLimits(
        max_risk_per_trade=0.02,
        max_daily_loss=0.05,
        max_drawdown=0.15,
        max_open_positions=10,
        max_total_exposure=0.80,
        max_probability_of_ruin=0.10,
    )
    manager = RiskManager(limits)

    decision = manager.evaluate(
        risk_fraction=0.015,
        daily_loss_fraction=0.02,
        drawdown_fraction=0.05,
        open_positions=4,
        total_exposure_fraction=0.60,
        probability_of_ruin=0.08,
    )

    assert decision.allowed is True


def test_rejects_negative_open_positions():
    manager = RiskManager()
    values = valid_inputs()
    values["open_positions"] = -1

    with pytest.raises(
        ValueError,
        match="OPEN_POSITIONS_MUST_BE_NON_NEGATIVE",
    ):
        manager.evaluate(**values)


def test_rejects_invalid_limit_configuration():
    with pytest.raises(
        ValueError,
        match="MAX_RISK_PER_TRADE",
    ):
        RiskLimits(max_risk_per_trade=0.0)


def test_risk_action_is_string_enum():
    assert RiskAction.ALLOW.value == "allow"
    assert str(RiskAction.ALLOW) == "allow"

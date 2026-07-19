import pytest

from jemba_core.pipeline.risk_pipeline import (
    RiskPipeline,
    RiskPipelineInput,
    RiskPipelineResult,
)
from jemba_core.risk_engine import (
    RiskAction,
    RiskLimits,
)


def valid_input(**overrides):
    values = {
        "risk_fraction": 0.01,
        "daily_loss_fraction": 0.01,
        "drawdown_fraction": 0.04,
        "open_positions": 2,
        "total_exposure_fraction": 0.40,
        "probability_of_ruin": 0.02,
        "kill_switch": False,
    }
    values.update(overrides)

    return RiskPipelineInput(**values)


def test_allows_signal_inside_risk_limits():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input())

    assert isinstance(result, RiskPipelineResult)
    assert result.approved is True
    assert result.decision.action is RiskAction.ALLOW
    assert result.reason is None


def test_blocks_signal_above_risk_per_trade():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(risk_fraction=0.02))

    assert result.approved is False
    assert result.decision.action is RiskAction.BLOCK
    assert result.reason == "RISK_PER_TRADE_LIMIT"


def test_blocks_signal_at_daily_loss_limit():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(daily_loss_fraction=0.03))

    assert result.approved is False
    assert result.reason == "DAILY_LOSS_LIMIT"


def test_blocks_signal_at_drawdown_limit():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(drawdown_fraction=0.10))

    assert result.approved is False
    assert result.reason == "MAX_DRAWDOWN_LIMIT"


def test_blocks_signal_at_maximum_positions():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(open_positions=5))

    assert result.approved is False
    assert result.reason == "MAX_OPEN_POSITIONS"


def test_blocks_signal_at_exposure_limit():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(total_exposure_fraction=1.0))

    assert result.approved is False
    assert result.reason == "TOTAL_EXPOSURE_LIMIT"


def test_blocks_signal_above_probability_of_ruin_limit():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(probability_of_ruin=0.06))

    assert result.approved is False
    assert result.reason == "PROBABILITY_OF_RUIN_LIMIT"


def test_kill_switch_blocks_everything():
    pipeline = RiskPipeline()

    result = pipeline.evaluate(valid_input(kill_switch=True))

    assert result.approved is False
    assert result.decision.action is RiskAction.KILL_SWITCH
    assert result.reason == "KILL_SWITCH_ACTIVE"


def test_can_execute_returns_boolean():
    pipeline = RiskPipeline()

    assert pipeline.can_execute(valid_input()) is True
    assert pipeline.can_execute(valid_input(kill_switch=True)) is False


def test_supports_custom_limits():
    pipeline = RiskPipeline(
        limits=RiskLimits(
            max_risk_per_trade=0.02,
            max_daily_loss=0.05,
            max_drawdown=0.15,
            max_open_positions=10,
            max_total_exposure=0.80,
            max_probability_of_ruin=0.10,
        )
    )

    result = pipeline.evaluate(
        valid_input(
            risk_fraction=0.015,
            daily_loss_fraction=0.02,
            drawdown_fraction=0.05,
            open_positions=4,
            total_exposure_fraction=0.60,
            probability_of_ruin=0.08,
        )
    )

    assert result.approved is True


def test_rejects_invalid_input_type():
    pipeline = RiskPipeline()

    with pytest.raises(
        TypeError,
        match="RISK_INPUT_MUST_BE_RISK_PIPELINE_INPUT",
    ):
        pipeline.evaluate({})


def test_rejects_manager_and_limits_together():
    from jemba_core.risk_engine import RiskManager

    with pytest.raises(
        ValueError,
        match="PROVIDE_RISK_MANAGER_OR_LIMITS_NOT_BOTH",
    ):
        RiskPipeline(
            risk_manager=RiskManager(),
            limits=RiskLimits(),
        )

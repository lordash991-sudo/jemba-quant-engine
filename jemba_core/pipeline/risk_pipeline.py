from __future__ import annotations

from dataclasses import dataclass

from jemba_core.risk_engine import (
    RiskAction,
    RiskDecision,
    RiskLimits,
    RiskManager,
)


@dataclass(frozen=True, slots=True)
class RiskPipelineInput:
    """Current portfolio and trade-risk state."""

    risk_fraction: float
    daily_loss_fraction: float
    drawdown_fraction: float
    open_positions: int
    total_exposure_fraction: float
    probability_of_ruin: float
    kill_switch: bool = False


@dataclass(frozen=True, slots=True)
class RiskPipelineResult:
    """Result returned before a trade reaches execution."""

    approved: bool
    decision: RiskDecision

    @property
    def reason(self) -> str | None:
        return self.decision.reason


class RiskPipeline:
    """
    Validate a proposed trade before execution.

    Every new signal must pass through this pipeline before it can
    reach position sizing or the execution engine.
    """

    def __init__(
        self,
        risk_manager: RiskManager | None = None,
        limits: RiskLimits | None = None,
    ) -> None:
        if risk_manager is not None and limits is not None:
            raise ValueError("PROVIDE_RISK_MANAGER_OR_LIMITS_NOT_BOTH")

        self._risk_manager = (
            risk_manager if risk_manager is not None else RiskManager(limits=limits)
        )

    def evaluate(
        self,
        risk_input: RiskPipelineInput,
    ) -> RiskPipelineResult:
        """Evaluate whether a proposed trade may proceed."""
        if not isinstance(risk_input, RiskPipelineInput):
            raise TypeError("RISK_INPUT_MUST_BE_RISK_PIPELINE_INPUT")

        decision = self._risk_manager.evaluate(
            risk_fraction=risk_input.risk_fraction,
            daily_loss_fraction=risk_input.daily_loss_fraction,
            drawdown_fraction=risk_input.drawdown_fraction,
            open_positions=risk_input.open_positions,
            total_exposure_fraction=(risk_input.total_exposure_fraction),
            probability_of_ruin=risk_input.probability_of_ruin,
            kill_switch=risk_input.kill_switch,
        )

        return RiskPipelineResult(
            approved=decision.action is RiskAction.ALLOW,
            decision=decision,
        )

    def can_execute(
        self,
        risk_input: RiskPipelineInput,
    ) -> bool:
        """Return only the execution permission."""
        return self.evaluate(risk_input).approved

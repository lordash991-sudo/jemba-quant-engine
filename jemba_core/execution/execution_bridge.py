from __future__ import annotations

from datetime import UTC, datetime

from jemba_core.execution.execution_request import (
    ExecutionRequest,
)
from jemba_core.execution.execution_result import (
    ExecutionResult,
)
from jemba_core.execution.fill_simulator import FillSimulator
from jemba_core.execution.order_validator import OrderValidator


class ExecutionBridge:
    """Validate approved decisions and simulate paper fills."""

    def __init__(
        self,
        *,
        validator: OrderValidator | None = None,
        fill_simulator: FillSimulator | None = None,
    ) -> None:
        self.validator = validator or OrderValidator()
        self.fill_simulator = fill_simulator or FillSimulator()

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        validation = self.validator.validate(request)

        if not validation.approved:
            return ExecutionResult(
                approved=False,
                symbol=request.symbol.strip().upper(),
                entry_price=float(request.entry_price),
                executed_price=0.0,
                quantity=0.0,
                notional=0.0,
                margin_used=0.0,
                commission=0.0,
                slippage=0.0,
                order_id=None,
                timestamp=datetime.now(UTC),
                reason=validation.primary_reason,
            )

        return self.fill_simulator.execute(request)

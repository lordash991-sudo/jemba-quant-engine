from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from jemba_core.execution.commission_model import (
    CommissionModel,
)
from jemba_core.execution.execution_request import (
    ExecutionRequest,
)
from jemba_core.execution.execution_result import (
    ExecutionResult,
)
from jemba_core.execution.slippage_model import (
    SlippageModel,
)


@dataclass(frozen=True, slots=True)
class FillSimulatorConfig:
    funding_periods: int = 0


class FillSimulator:
    def __init__(
        self,
        *,
        slippage_model: SlippageModel | None = None,
        commission_model: CommissionModel | None = None,
        config: FillSimulatorConfig | None = None,
    ) -> None:
        self.slippage_model = slippage_model or SlippageModel()
        self.commission_model = commission_model or CommissionModel()
        self.config = config or FillSimulatorConfig()

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        slippage = self.slippage_model.calculate(
            price=request.entry_price,
            side=request.side,
            volatility=request.volatility,
        )

        executed_price = slippage.executed_price
        notional = executed_price * request.quantity
        margin_used = notional / request.leverage

        commission = self.commission_model.calculate(
            notional=notional,
            order_type=request.order_type,
            funding_periods=self.config.funding_periods,
        )

        return ExecutionResult(
            approved=True,
            symbol=request.symbol.strip().upper(),
            entry_price=float(request.entry_price),
            executed_price=float(executed_price),
            quantity=float(request.quantity),
            notional=float(notional),
            margin_used=float(margin_used),
            commission=float(commission.total_cost),
            slippage=float(slippage.amount),
            order_id=uuid.uuid4().hex,
            timestamp=datetime.now(UTC),
            reason=None,
        )

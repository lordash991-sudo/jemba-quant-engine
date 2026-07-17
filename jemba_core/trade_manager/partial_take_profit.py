from dataclasses import dataclass


@dataclass(frozen=True)
class PartialTakeProfitResult:
    triggered: bool
    reason: str | None = None


def check_partial_take_profit(
    current_rr: float,
    trigger_rr: float,
) -> PartialTakeProfitResult:
    """
    Activa un cierre parcial cuando se alcanza
    un determinado múltiplo de riesgo.
    """

    if trigger_rr <= 0:
        raise ValueError("TRIGGER_RR_MUST_BE_POSITIVE")

    if current_rr >= trigger_rr:
        return PartialTakeProfitResult(
            True,
            "PARTIAL_TAKE_PROFIT",
        )

    return PartialTakeProfitResult(False)
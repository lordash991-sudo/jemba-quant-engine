from jemba_core.engine.quant_orchestrator import QuantOrchestrator


def test_quant_orchestrator_can_initialize():
    q = QuantOrchestrator(
        account_balance=10000,
        min_confidence=0.70,
    )

    assert q is not None


def test_quant_orchestrator_best_opportunity_empty():
    q = QuantOrchestrator(
        account_balance=10000,
        min_confidence=0.70,
    )

    result = q.best_opportunity([])

    assert result is None

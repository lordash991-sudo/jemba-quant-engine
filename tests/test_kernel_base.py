from jemba_core.kernel.container import Container
from jemba_core.kernel.modes import PAPER, LIVE, BACKTEST, SIMULATION, VALID_MODES


def test_container_initializes():
    c = Container()

    assert c.config is None
    assert c.provider is None
    assert c.pipeline is None
    assert c.execution is None
    assert c.scheduler is None


def test_modes():
    assert PAPER in VALID_MODES
    assert LIVE in VALID_MODES
    assert BACKTEST in VALID_MODES
    assert SIMULATION in VALID_MODES

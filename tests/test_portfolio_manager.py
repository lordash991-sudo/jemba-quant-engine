from jemba_core.portfolio_manager import (
    PortfolioManager,
    PortfolioState,
)


def test_can_open():

    manager = PortfolioManager()

    state = PortfolioState(
        capital=10000,
        used_margin=1000,
        open_positions=1,
    )

    assert manager.can_open(state,1000)


def test_margin_limit():

    manager = PortfolioManager()

    state = PortfolioState(
        capital=10000,
        used_margin=7900,
        open_positions=1,
    )

    assert not manager.can_open(state,500)


def test_position_limit():

    manager = PortfolioManager(max_positions=2)

    state = PortfolioState(
        capital=10000,
        used_margin=1000,
        open_positions=2,
        max_positions=2,
    )

    assert not manager.can_open(state,100)


def test_allocate():

    manager = PortfolioManager()

    state = PortfolioState(
        capital=10000,
        used_margin=1000,
        open_positions=1,
    )

    new_state = manager.allocate(
        state,
        500,
    )

    assert new_state.used_margin == 1500
    assert new_state.open_positions == 2


def test_free_margin():

    manager = PortfolioManager()

    state = PortfolioState(
        capital=10000,
        used_margin=3500,
        open_positions=2,
    )

    assert manager.free_margin(state) == 6500

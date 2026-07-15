import pytest

from jemba_core.trade_manager.trailing_manager import (
    update_trailing_stop,
)


def test_long_moves_up():

    assert (
        update_trailing_stop(
            95,
            98,
            "long",
        )
        == 98
    )


def test_long_never_moves_down():

    assert (
        update_trailing_stop(
            98,
            95,
            "long",
        )
        == 98
    )


def test_short_moves_down():

    assert (
        update_trailing_stop(
            105,
            102,
            "short",
        )
        == 102
    )


def test_short_never_moves_up():

    assert (
        update_trailing_stop(
            102,
            105,
            "short",
        )
        == 102
    )


def test_invalid_side():

    with pytest.raises(ValueError):
        update_trailing_stop(
            95,
            96,
            "btc",
        )

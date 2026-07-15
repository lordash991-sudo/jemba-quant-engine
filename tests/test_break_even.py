import pytest

from jemba_core.trade_manager.break_even import move_stop_to_break_even


def test_long_moves_to_be():

    assert (
        move_stop_to_break_even(
            entry_price=100,
            stop_price=95,
            current_price=105,
        )
        == 100
    )


def test_long_not_yet():

    assert (
        move_stop_to_break_even(
            entry_price=100,
            stop_price=95,
            current_price=103,
        )
        == 95
    )


def test_short_moves_to_be():

    assert (
        move_stop_to_break_even(
            entry_price=100,
            stop_price=105,
            current_price=95,
        )
        == 100
    )


def test_invalid_trigger():

    with pytest.raises(ValueError):
        move_stop_to_break_even(
            100,
            95,
            101,
            trigger_r=0,
        )


def test_invalid_stop():

    with pytest.raises(ValueError):
        move_stop_to_break_even(
            100,
            100,
            110,
        )

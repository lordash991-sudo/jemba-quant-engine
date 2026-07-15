import math

import pytest

from jemba_core.risk import (
    trailing_long,
    trailing_short,
    update_trailing_stop,
)


def test_long_trailing_stop_moves_up():
    result = trailing_long(
        current_stop=95.0,
        highest_price=110.0,
        atr=3.0,
        multiplier=2.0,
    )

    assert result == pytest.approx(104.0)


def test_long_trailing_stop_never_moves_down():
    result = trailing_long(
        current_stop=105.0,
        highest_price=108.0,
        atr=3.0,
        multiplier=2.0,
    )

    assert result == pytest.approx(105.0)


def test_short_trailing_stop_moves_down():
    result = trailing_short(
        current_stop=105.0,
        lowest_price=90.0,
        atr=3.0,
        multiplier=2.0,
    )

    assert result == pytest.approx(96.0)


def test_short_trailing_stop_never_moves_up():
    result = trailing_short(
        current_stop=95.0,
        lowest_price=92.0,
        atr=3.0,
        multiplier=2.0,
    )

    assert result == pytest.approx(95.0)


def test_wrapper_updates_long_and_short():
    assert update_trailing_stop(
        current_stop=95.0,
        reference_price=110.0,
        atr=3.0,
        multiplier=2.0,
        side="long",
    ) == pytest.approx(104.0)

    assert update_trailing_stop(
        current_stop=105.0,
        reference_price=90.0,
        atr=3.0,
        multiplier=2.0,
        side="short",
    ) == pytest.approx(96.0)


def test_rejects_invalid_side():
    with pytest.raises(
        ValueError,
        match="INVALID_SIDE",
    ):
        update_trailing_stop(
            current_stop=95.0,
            reference_price=110.0,
            atr=3.0,
            multiplier=2.0,
            side="flat",
        )


def test_rejects_non_finite_atr():
    with pytest.raises(
        ValueError,
        match="ATR_MUST_BE_FINITE",
    ):
        trailing_long(
            current_stop=95.0,
            highest_price=110.0,
            atr=math.inf,
            multiplier=2.0,
        )


def test_rejects_negative_long_current_stop():
    with pytest.raises(
        ValueError,
        match="CURRENT_STOP_MUST_BE_NON_NEGATIVE",
    ):
        trailing_long(
            current_stop=-1.0,
            highest_price=110.0,
            atr=3.0,
            multiplier=2.0,
        )

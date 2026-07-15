import math

import pytest

from jemba_core.risk import (
    chandelier_exit,
    chandelier_long,
    chandelier_short,
)


def test_calculates_long_chandelier():
    assert chandelier_long(
        highest_high=120.0,
        atr=5.0,
        multiplier=3.0,
    ) == pytest.approx(105.0)


def test_calculates_short_chandelier():
    assert chandelier_short(
        lowest_low=80.0,
        atr=5.0,
        multiplier=3.0,
    ) == pytest.approx(95.0)


def test_wrapper_selects_correct_side():
    assert chandelier_exit(
        reference_price=120.0,
        atr=5.0,
        multiplier=3.0,
        side="long",
    ) == pytest.approx(105.0)

    assert chandelier_exit(
        reference_price=80.0,
        atr=5.0,
        multiplier=3.0,
        side="short",
    ) == pytest.approx(95.0)


def test_rejects_invalid_side():
    with pytest.raises(
        ValueError,
        match="INVALID_SIDE",
    ):
        chandelier_exit(
            reference_price=100.0,
            atr=5.0,
            multiplier=3.0,
            side="neutral",
        )


@pytest.mark.parametrize(
    "value",
    [0.0, -1.0],
)
def test_rejects_non_positive_reference(value):
    with pytest.raises(
        ValueError,
        match="HIGHEST_HIGH_MUST_BE_POSITIVE",
    ):
        chandelier_long(
            highest_high=value,
            atr=5.0,
            multiplier=3.0,
        )


def test_rejects_non_finite_atr():
    with pytest.raises(
        ValueError,
        match="ATR_MUST_BE_FINITE",
    ):
        chandelier_long(
            highest_high=120.0,
            atr=math.nan,
            multiplier=3.0,
        )


def test_rejects_negative_long_stop():
    with pytest.raises(
        ValueError,
        match="LONG_STOP_CANNOT_BE_NEGATIVE",
    ):
        chandelier_long(
            highest_high=5.0,
            atr=4.0,
            multiplier=2.0,
        )

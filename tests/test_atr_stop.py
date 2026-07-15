import math

import pytest

from jemba_core.risk import (
    atr_long_stop,
    atr_short_stop,
    atr_stop,
    atr_stop_distance,
)


def test_calculates_long_stop():
    assert atr_stop(
        entry_price=100.0,
        atr=2.0,
        multiplier=2.0,
        side="long",
    ) == pytest.approx(96.0)


def test_calculates_short_stop():
    assert atr_stop(
        entry_price=100.0,
        atr=2.0,
        multiplier=2.0,
        side="short",
    ) == pytest.approx(104.0)


def test_direct_long_and_short_functions():
    assert atr_long_stop(100.0, 2.0, 2.0) == 96.0
    assert atr_short_stop(100.0, 2.0, 2.0) == 104.0


def test_calculates_stop_distance():
    assert atr_stop_distance(
        atr=2.5,
        multiplier=3.0,
    ) == pytest.approx(7.5)


def test_side_is_case_insensitive():
    assert atr_stop(
        100.0,
        2.0,
        2.0,
        " LONG ",
    ) == pytest.approx(96.0)


@pytest.mark.parametrize(
    "atr",
    [0.0, -1.0],
)
def test_rejects_non_positive_atr(atr):
    with pytest.raises(
        ValueError,
        match="ATR_MUST_BE_POSITIVE",
    ):
        atr_stop(100.0, atr, 2.0, "long")


@pytest.mark.parametrize(
    "atr",
    [math.nan, math.inf],
)
def test_rejects_non_finite_atr(atr):
    with pytest.raises(
        ValueError,
        match="ATR_MUST_BE_FINITE",
    ):
        atr_stop(100.0, atr, 2.0, "long")


def test_rejects_invalid_multiplier():
    with pytest.raises(
        ValueError,
        match="MULTIPLIER_MUST_BE_POSITIVE",
    ):
        atr_stop(100.0, 2.0, 0.0, "long")


def test_rejects_invalid_side():
    with pytest.raises(
        ValueError,
        match="INVALID_SIDE",
    ):
        atr_stop(100.0, 2.0, 2.0, "buy")


def test_rejects_negative_long_stop():
    with pytest.raises(
        ValueError,
        match="LONG_STOP_CANNOT_BE_NEGATIVE",
    ):
        atr_long_stop(
            entry_price=5.0,
            atr=4.0,
            multiplier=2.0,
        )

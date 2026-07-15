import math

import pytest

from jemba_core.risk_engine import (
    atr_stop,
    atr_stop_distance,
)


def test_calculates_long_atr_stop():
    result = atr_stop(
        entry_price=100.0,
        atr=2.0,
        multiplier=2.0,
        side="long",
    )

    assert result == pytest.approx(96.0)


def test_calculates_short_atr_stop():
    result = atr_stop(
        entry_price=100.0,
        atr=2.0,
        multiplier=2.0,
        side="short",
    )

    assert result == pytest.approx(104.0)


def test_side_is_case_insensitive():
    assert atr_stop(
        entry_price=100.0,
        atr=2.0,
        multiplier=2.0,
        side=" LONG ",
    ) == pytest.approx(96.0)


def test_calculates_stop_distance():
    assert atr_stop_distance(
        atr=2.5,
        multiplier=3.0,
    ) == pytest.approx(7.5)


@pytest.mark.parametrize(
    ("atr", "expected_message"),
    [
        (0.0, "ATR_MUST_BE_POSITIVE"),
        (-1.0, "ATR_MUST_BE_POSITIVE"),
        (math.nan, "ATR_MUST_BE_FINITE"),
        (math.inf, "ATR_MUST_BE_FINITE"),
    ],
)
def test_rejects_invalid_atr(
    atr,
    expected_message,
):
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        atr_stop(
            entry_price=100.0,
            atr=atr,
            multiplier=2.0,
            side="long",
        )


@pytest.mark.parametrize(
    ("multiplier", "expected_message"),
    [
        (0.0, "MULTIPLIER_MUST_BE_POSITIVE"),
        (-1.0, "MULTIPLIER_MUST_BE_POSITIVE"),
        (math.nan, "MULTIPLIER_MUST_BE_FINITE"),
        (math.inf, "MULTIPLIER_MUST_BE_FINITE"),
    ],
)
def test_rejects_invalid_multiplier(
    multiplier,
    expected_message,
):
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        atr_stop(
            entry_price=100.0,
            atr=2.0,
            multiplier=multiplier,
            side="long",
        )


def test_rejects_invalid_side():
    with pytest.raises(
        ValueError,
        match="INVALID_SIDE",
    ):
        atr_stop(
            entry_price=100.0,
            atr=2.0,
            multiplier=2.0,
            side="buy",
        )


def test_rejects_non_string_side():
    with pytest.raises(
        TypeError,
        match="SIDE_MUST_BE_STRING",
    ):
        atr_stop(
            entry_price=100.0,
            atr=2.0,
            multiplier=2.0,
            side=1,
        )


def test_rejects_non_positive_entry_price():
    with pytest.raises(
        ValueError,
        match="ENTRY_PRICE_MUST_BE_POSITIVE",
    ):
        atr_stop(
            entry_price=0.0,
            atr=2.0,
            multiplier=2.0,
            side="long",
        )


def test_rejects_negative_long_stop():
    with pytest.raises(
        ValueError,
        match="LONG_STOP_CANNOT_BE_NEGATIVE",
    ):
        atr_stop(
            entry_price=5.0,
            atr=4.0,
            multiplier=2.0,
            side="long",
        )

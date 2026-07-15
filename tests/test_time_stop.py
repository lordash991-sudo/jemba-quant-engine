from datetime import UTC, datetime, timedelta

import pytest

from jemba_core.trade_manager.time_stop import check_time_stop


def test_no_close_before_limit():
    opened = datetime.now(UTC)

    result = check_time_stop(
        opened_at=opened,
        current_time=opened + timedelta(minutes=10),
        max_minutes=30,
    )

    assert result.should_close is False
    assert result.reason is None


def test_close_by_minutes():
    opened = datetime.now(UTC)

    result = check_time_stop(
        opened_at=opened,
        current_time=opened + timedelta(minutes=35),
        max_minutes=30,
    )

    assert result.should_close is True
    assert result.reason == "TIME_STOP"


def test_close_exactly_at_minute_limit():
    opened = datetime.now(UTC)

    result = check_time_stop(
        opened_at=opened,
        current_time=opened + timedelta(minutes=30),
        max_minutes=30,
    )

    assert result.should_close is True
    assert result.reason == "TIME_STOP"


def test_close_by_bars():
    opened = datetime.now(UTC)

    result = check_time_stop(
        opened_at=opened,
        current_time=opened + timedelta(minutes=1),
        max_bars=24,
        bars_elapsed=24,
    )

    assert result.should_close is True
    assert result.reason == "BAR_STOP"


def test_no_close_before_bar_limit():
    opened = datetime.now(UTC)

    result = check_time_stop(
        opened_at=opened,
        current_time=opened + timedelta(minutes=1),
        max_bars=24,
        bars_elapsed=23,
    )

    assert result.should_close is False


def test_requires_bars_elapsed():
    opened = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="BARS_ELAPSED_REQUIRED",
    ):
        check_time_stop(
            opened_at=opened,
            current_time=opened,
            max_bars=24,
        )


def test_rejects_invalid_minutes():
    opened = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="MAX_MINUTES_MUST_BE_POSITIVE",
    ):
        check_time_stop(
            opened_at=opened,
            current_time=opened,
            max_minutes=0,
        )


def test_rejects_invalid_max_bars():
    opened = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="MAX_BARS_MUST_BE_POSITIVE",
    ):
        check_time_stop(
            opened_at=opened,
            current_time=opened,
            max_bars=0,
            bars_elapsed=0,
        )


def test_rejects_current_time_before_open():
    opened = datetime.now(UTC)

    with pytest.raises(
        ValueError,
        match="CURRENT_TIME_BEFORE_OPEN",
    ):
        check_time_stop(
            opened_at=opened,
            current_time=opened - timedelta(minutes=1),
            max_minutes=10,
        )

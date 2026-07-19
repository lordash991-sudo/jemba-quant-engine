import pytest

from jemba_core.portfolio.correlation_manager import (
    CorrelationManager,
)


def test_allows_low_correlation():
    manager = CorrelationManager(max_correlation=0.80)

    result = manager.check(0.45)

    assert result.allowed is True
    assert result.correlation == pytest.approx(0.45)
    assert result.reason is None


def test_blocks_high_positive_correlation():
    manager = CorrelationManager(max_correlation=0.80)

    result = manager.check(0.90)

    assert result.allowed is False
    assert result.reason == "CORRELATION_LIMIT_REACHED"


def test_blocks_high_negative_correlation_in_same_direction():
    manager = CorrelationManager(max_correlation=0.80)

    result = manager.check(
        -0.90,
        same_direction=True,
    )

    assert result.allowed is False


def test_opposite_direction_uses_signed_correlation():
    manager = CorrelationManager(max_correlation=0.80)

    result = manager.check(
        -0.90,
        same_direction=False,
    )

    assert result.allowed is True


def test_allows_exact_limit():
    manager = CorrelationManager(max_correlation=0.80)

    result = manager.check(0.80)

    assert result.allowed is True


def test_rejects_invalid_correlation():
    manager = CorrelationManager()

    with pytest.raises(
        ValueError,
        match="CORRELATION_MUST_BE_BETWEEN_MINUS_1_AND_1",
    ):
        manager.check(1.20)


def test_rejects_non_finite_correlation():
    manager = CorrelationManager()

    with pytest.raises(
        ValueError,
        match="CORRELATION_MUST_BE_FINITE",
    ):
        manager.check(float("nan"))


def test_rejects_invalid_max_correlation():
    with pytest.raises(
        ValueError,
        match="MAX_CORRELATION_MUST_BE_BETWEEN_0_AND_1",
    ):
        CorrelationManager(max_correlation=1.50)


def test_rejects_invalid_direction_type():
    manager = CorrelationManager()

    with pytest.raises(
        TypeError,
        match="SAME_DIRECTION_MUST_BE_BOOLEAN",
    ):
        manager.check(0.50, same_direction="yes")

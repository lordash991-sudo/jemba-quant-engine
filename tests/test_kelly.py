import pytest

from jemba_core.portfolio_optimizer import kelly_fraction


def test_calculates_full_kelly():
    value = kelly_fraction(
        win_rate=0.60,
        payoff_ratio=2.0,
    )

    assert value == pytest.approx(0.40)


def test_supports_fractional_kelly():
    value = kelly_fraction(
        win_rate=0.60,
        payoff_ratio=2.0,
        fraction=0.50,
    )

    assert value == pytest.approx(0.20)


def test_negative_edge_returns_zero():
    value = kelly_fraction(
        win_rate=0.40,
        payoff_ratio=1.0,
    )

    assert value == 0.0


def test_applies_maximum_cap():
    value = kelly_fraction(
        win_rate=0.80,
        payoff_ratio=3.0,
        maximum=0.25,
    )

    assert value == 0.25


def test_rejects_invalid_payoff():
    with pytest.raises(
        ValueError,
        match="PAYOFF_RATIO_MUST_BE_POSITIVE",
    ):
        kelly_fraction(
            win_rate=0.60,
            payoff_ratio=0.0,
        )

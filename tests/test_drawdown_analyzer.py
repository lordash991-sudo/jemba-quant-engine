import pytest

from jemba_core.montecarlo.drawdown_analyzer import (
    DrawdownAnalyzer,
)


def test_no_drawdown_on_monotonic_curve():
    analyzer = DrawdownAnalyzer()

    result = analyzer.analyze([100, 110, 120, 130])

    assert result.max_drawdown == 0.0
    assert result.average_drawdown == 0.0
    assert result.max_duration == 0
    assert result.max_recovery_duration == 0
    assert result.episode_count == 0
    assert result.episodes == ()


def test_detects_recovered_drawdown():
    analyzer = DrawdownAnalyzer()

    result = analyzer.analyze([100, 120, 90, 100, 120])

    assert result.episode_count == 1
    assert result.max_drawdown == pytest.approx(0.25)

    episode = result.episodes[0]

    assert episode.start_index == 1
    assert episode.trough_index == 2
    assert episode.recovery_index == 4
    assert episode.duration == 3
    assert episode.recovery_duration == 2


def test_detects_unrecovered_drawdown():
    analyzer = DrawdownAnalyzer()

    result = analyzer.analyze([100, 120, 110, 80])

    assert result.episode_count == 1
    assert result.max_drawdown == pytest.approx(1 / 3)

    episode = result.episodes[0]

    assert episode.recovery_index is None
    assert episode.recovery_duration is None
    assert result.max_recovery_duration is None


def test_detects_multiple_drawdowns():
    analyzer = DrawdownAnalyzer()

    result = analyzer.analyze([100, 90, 100, 80, 110])

    assert result.episode_count == 2
    assert result.max_drawdown == pytest.approx(0.20)
    assert result.average_drawdown == pytest.approx(0.15)
    assert result.max_duration == 2


def test_analyze_many():
    analyzer = DrawdownAnalyzer()

    results = analyzer.analyze_many(
        [
            [100, 90, 100],
            [100, 80, 120],
        ]
    )

    assert len(results) == 2
    assert results[0].max_drawdown == pytest.approx(0.10)
    assert results[1].max_drawdown == pytest.approx(0.20)


def test_percentile_max_drawdown():
    analyzer = DrawdownAnalyzer()

    stats = analyzer.analyze_many(
        [
            [100, 90, 100],
            [100, 80, 100],
            [100, 70, 100],
            [100, 60, 100],
        ]
    )

    assert analyzer.percentile_max_drawdown(
        stats,
        50,
    ) == pytest.approx(0.20)

    assert analyzer.percentile_max_drawdown(
        stats,
        100,
    ) == pytest.approx(0.40)


def test_rejects_empty_curve():
    analyzer = DrawdownAnalyzer()

    with pytest.raises(
        ValueError,
        match="EQUITY_CURVE_CANNOT_BE_EMPTY",
    ):
        analyzer.analyze([])


def test_rejects_non_positive_equity():
    analyzer = DrawdownAnalyzer()

    with pytest.raises(
        ValueError,
        match="EQUITY_VALUE_MUST_BE_POSITIVE",
    ):
        analyzer.analyze([100, 0, 90])


def test_rejects_non_finite_equity():
    analyzer = DrawdownAnalyzer()

    with pytest.raises(
        ValueError,
        match="EQUITY_VALUE_MUST_BE_FINITE",
    ):
        analyzer.analyze([100, float("nan")])


def test_rejects_empty_collection():
    analyzer = DrawdownAnalyzer()

    with pytest.raises(
        ValueError,
        match="EQUITY_CURVES_CANNOT_BE_EMPTY",
    ):
        analyzer.analyze_many([])


def test_rejects_invalid_percentile():
    analyzer = DrawdownAnalyzer()

    stats = analyzer.analyze_many([[100, 90, 100]])

    with pytest.raises(
        ValueError,
        match="PERCENTILE_MUST_BE_BETWEEN_0_AND_100",
    ):
        analyzer.percentile_max_drawdown(
            stats,
            101,
        )

from __future__ import annotations

import pandas as pd
import pytest

from jemba_core.labels.po3_label_generator import (
    PO3Label,
    PO3LabelConfig,
    PO3LabelGenerator,
)


def make_frame(
    *,
    signal: int,
    future_highs: list[float],
    future_lows: list[float],
    future_closes: list[float] | None = None,
) -> pd.DataFrame:
    closes = future_closes or [
        100.0
        for _ in future_highs
    ]

    rows = [
        {
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "ATR": 1.0,
            "PO3_SIGNAL": signal,
        }
    ]

    for high, low, close in zip(
        future_highs,
        future_lows,
        closes,
    ):
        rows.append(
            {
                "open": 100.0,
                "high": high,
                "low": low,
                "close": close,
                "ATR": 1.0,
                "PO3_SIGNAL": 0,
            }
        )

    return pd.DataFrame(rows)


def test_long_take_profit() -> None:
    frame = make_frame(
        signal=1,
        future_highs=[101.0, 102.5],
        future_lows=[99.5, 99.7],
    )

    generator = PO3LabelGenerator(
        PO3LabelConfig(
            horizon_bars=4,
            stop_atr=1.0,
            target_atr=2.0,
        )
    )

    result = generator.generate(frame)

    assert result.loc[0, "LABEL"] == int(
        PO3Label.TAKE_PROFIT
    )

    assert result.loc[0, "HIT_TP"] == 1
    assert result.loc[0, "HIT_SL"] == 0
    assert result.loc[0, "R_MULTIPLE"] == pytest.approx(2.0)


def test_long_stop_loss() -> None:
    frame = make_frame(
        signal=1,
        future_highs=[100.5],
        future_lows=[98.5],
    )

    generator = PO3LabelGenerator()

    result = generator.generate(frame)

    assert result.loc[0, "LABEL"] == int(
        PO3Label.STOP_LOSS
    )

    assert result.loc[0, "HIT_SL"] == 1
    assert result.loc[0, "R_MULTIPLE"] == pytest.approx(-1.0)


def test_short_take_profit() -> None:
    frame = make_frame(
        signal=-1,
        future_highs=[100.5, 100.2],
        future_lows=[99.4, 97.5],
    )

    generator = PO3LabelGenerator()

    result = generator.generate(frame)

    assert result.loc[0, "LABEL"] == int(
        PO3Label.TAKE_PROFIT
    )

    assert result.loc[0, "HIT_TP"] == 1


def test_short_stop_loss() -> None:
    frame = make_frame(
        signal=-1,
        future_highs=[101.5],
        future_lows=[99.7],
    )

    generator = PO3LabelGenerator()

    result = generator.generate(frame)

    assert result.loc[0, "LABEL"] == int(
        PO3Label.STOP_LOSS
    )


def test_signal_expires() -> None:
    frame = make_frame(
        signal=1,
        future_highs=[100.4, 100.7],
        future_lows=[99.4, 99.2],
        future_closes=[100.2, 100.3],
    )

    generator = PO3LabelGenerator(
        PO3LabelConfig(
            horizon_bars=2,
        )
    )

    result = generator.generate(frame)

    assert result.loc[0, "LABEL"] == int(
        PO3Label.EXPIRED
    )

    assert result.loc[0, "EXPIRED"] == 1


def test_ambiguous_candle_defaults_to_stop() -> None:
    frame = make_frame(
        signal=1,
        future_highs=[103.0],
        future_lows=[98.0],
    )

    generator = PO3LabelGenerator(
        PO3LabelConfig(
            ambiguous_policy="stop_first",
        )
    )

    result = generator.generate(frame)

    assert result.loc[0, "LABEL"] == int(
        PO3Label.STOP_LOSS
    )

    assert result.loc[0, "AMBIGUOUS_HIT"] == 1


def test_training_dataset_only_contains_signals() -> None:
    frame = make_frame(
        signal=1,
        future_highs=[102.5],
        future_lows=[99.5],
    )

    generator = PO3LabelGenerator()

    dataset = generator.training_dataset(
        frame
    )

    assert len(dataset) == 1
    assert dataset["LABEL"].notna().all()


def test_missing_columns_raise_error() -> None:
    generator = PO3LabelGenerator()

    with pytest.raises(
        ValueError,
        match="MISSING_LABEL_COLUMNS",
    ):
        generator.generate(
            pd.DataFrame(
                {
                    "close": [100.0],
                }
            )
        )


def test_invalid_configuration_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="HORIZON_BARS",
    ):
        PO3LabelConfig(
            horizon_bars=0,
        )
from __future__ import annotations

import pandas as pd

from jemba_core.ai.label_generator import LabelGenerator


def sample():
    return pd.DataFrame(
        {
            "close": [100, 105, 103, 110],
        }
    )


def test_label_generator_creates_target():
    result = LabelGenerator(horizon=1).transform(sample())

    assert "future_close" in result.columns
    assert "future_return" in result.columns
    assert "target" in result.columns
    assert list(result["target"]) == [1, 0, 1]


def test_label_generator_requires_close():
    df = pd.DataFrame({"open": [1, 2, 3]})

    try:
        LabelGenerator().transform(df)
    except ValueError as error:
        assert "Missing 'close' column" in str(error)
    else:
        raise AssertionError("Expected ValueError")

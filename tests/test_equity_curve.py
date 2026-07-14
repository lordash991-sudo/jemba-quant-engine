import numpy as np
import pytest

from jemba_core.quant import EquityCurve


def test_builds_equity_curve_from_pnl():
    curve = EquityCurve(
        initial_equity=1000.0,
        pnl=[100.0, -50.0, 25.0],
    )

    np.testing.assert_allclose(
        curve.equity(),
        [1000.0, 1100.0, 1050.0, 1075.0],
    )

    assert curve.final_equity() == 1075.0
    assert len(curve) == 3


def test_appends_and_extends_pnl():
    curve = EquityCurve(initial_equity=500.0)

    curve.append(50.0)
    curve.extend([-20.0, 10.0])

    np.testing.assert_allclose(
        curve.pnl(),
        [50.0, -20.0, 10.0],
    )


def test_rejects_non_finite_pnl():
    curve = EquityCurve()

    with pytest.raises(
        ValueError,
        match="PNL_MUST_BE_FINITE",
    ):
        curve.append(np.nan)

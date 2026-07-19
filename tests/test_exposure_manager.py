import pytest

from jemba_core.portfolio.exposure_manager import ExposureManager

manager = ExposureManager()

def test_trade_allowed():
    result = manager.check(0.20,0.10)
    assert result.allowed is True
    assert result.exposure == pytest.approx(0.30)

def test_trade_blocked():
    result = manager.check(0.50,0.20)
    assert result.allowed is False
    assert result.exposure == 0.70

def test_invalid_current():
    with pytest.raises(ValueError):
        manager.check(-1,0.1)

def test_invalid_position():
    with pytest.raises(ValueError):
        manager.check(0.2,-1)

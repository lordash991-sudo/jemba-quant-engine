import pytest

from jemba_core.portfolio.capital_allocator import CapitalAllocator

allocator = CapitalAllocator()

def test_low_confidence():
    result = allocator.allocate(0.50)
    assert result.risk_percent == 0.00

def test_medium_confidence():
    result = allocator.allocate(0.75)
    assert result.risk_percent == 1.00

def test_high_confidence():
    result = allocator.allocate(0.98)
    assert result.risk_percent == 3.00

def test_invalid_confidence():
    with pytest.raises(ValueError):
        allocator.allocate(1.5)

import pytest
from core.calculations.beam_calculation import calculate_moment

def test_moment_calculation():
    assert calculate_moment(100, 5) == 125.0  # (100 * 5) / 4 = 125
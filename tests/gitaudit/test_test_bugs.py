import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import test_bugs


def test_divide_valid():
    assert test_bugs.divide(10, 2) == 5.0
    assert test_bugs.divide(7, 2) == 3.5
    assert test_bugs.divide(0, 5) == 0.0


def test_divide_by_zero():
    assert test_bugs.divide(10, 0) is None
    assert test_bugs.divide(0, 0) is None

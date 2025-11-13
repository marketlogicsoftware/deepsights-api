"""
Unit tests for run_in_parallel utility.
"""

import pytest

from deepsights.utils._utils import run_in_parallel


def test_run_in_parallel_preserves_order():
    result = run_in_parallel(lambda x: x * 2, [1, 2, 3], max_workers=3)
    assert result == [2, 4, 6]


def test_run_in_parallel_propagates_exception():
    def f(x):
        if x == 2:
            raise ValueError("boom")
        return x

    with pytest.raises(ValueError):
        run_in_parallel(f, [1, 2, 3], max_workers=3)

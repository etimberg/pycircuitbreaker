import pytest

from pycircuitbreaker import circuit


def test_decorator_raises_error_if_no_callable_passed():
    with pytest.raises(ValueError):
        circuit('not a function')

from unittest import mock

import pytest

from pycircuitbreaker import CircuitBreaker, CircuitBreakerState


@pytest.fixture()
def error_func():
    def raises_error():
        raise IOError
    return raises_error


def test_breaker_starts_closed():
    breaker = CircuitBreaker()
    assert breaker.state == CircuitBreakerState.CLOSED


def test_breaker_opens_after_specified_number_of_errors(error_func):
    breaker = CircuitBreaker(error_threshold=2)

    with pytest.raises(IOError):
        breaker.call(error_func)
    assert breaker.state == CircuitBreakerState.CLOSED

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN

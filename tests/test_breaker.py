from time import sleep

import pytest

from pycircuitbreaker import CircuitBreaker, CircuitBreakerState


@pytest.fixture()
def error_func():
    def raises_error():
        raise IOError

    return raises_error


@pytest.fixture()
def success_func():
    def success():
        pass

    return success


@pytest.fixture()
def half_open_breaker(error_func):
    breaker = CircuitBreaker(
        error_threshold=1, recovery_timeout=1, recovery_threshold=2
    )

    with pytest.raises(IOError):
        breaker.call(error_func)

    sleep(1)

    return breaker


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


def test_breaker_recloses_after_recovery_time(error_func):
    breaker = CircuitBreaker(error_threshold=1, recovery_timeout=1)

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN

    sleep(1)
    assert breaker.state == CircuitBreakerState.HALF_OPEN


def test_half_open_breaker_fully_opens_after_recovery_threshold(
    half_open_breaker, success_func
):
    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.HALF_OPEN

    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.CLOSED


def test_exception_whitelist(error_func):
    breaker = CircuitBreaker(
        error_threshold=1, exception_whitelist=[IOError], recovery_timeout=1
    )
    breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.CLOSED


def test_exception_whitelist_supports_inheritance(error_func):
    breaker = CircuitBreaker(
        error_threshold=1, exception_whitelist=[Exception], recovery_timeout=1
    )
    breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.CLOSED


def test_exception_blacklist_filters_errors(error_func):
    # When the blacklist is specified, only those errors are caught
    breaker = CircuitBreaker(
        error_threshold=1, exception_blacklist=[ValueError], recovery_timeout=1
    )
    breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.CLOSED


def test_exception_blacklist_supports_inheritance(error_func):
    # When the blacklist is specified, only those errors are caught
    breaker = CircuitBreaker(
        error_threshold=1, exception_blacklist=[Exception], recovery_timeout=1
    )

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN

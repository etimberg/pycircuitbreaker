from time import sleep
from unittest import mock

import pytest

from pycircuitbreaker import (
    CircuitBreaker,
    CircuitBreakerException,
    CircuitBreakerState,
)


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


def test_error_resets_reclose_state(half_open_breaker, error_func, success_func):
    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.HALF_OPEN

    with pytest.raises(IOError):
        half_open_breaker.call(error_func)

    assert half_open_breaker.state == CircuitBreakerState.OPEN
    assert half_open_breaker.error_count == 2
    assert half_open_breaker.success_count == 0

    sleep(1)

    # If the count of success functions was correctly reset on error,
    # we should expect to be back at half open as there is only 1 success at this point
    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.HALF_OPEN


def test_half_open_breaker_closes_after_recovery_threshold(
    half_open_breaker, success_func
):
    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.HALF_OPEN
    assert half_open_breaker.success_count == 1

    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.CLOSED
    assert half_open_breaker.success_count == 2


def test_error_during_recovery_period_resets_recovery_count(
    half_open_breaker, error_func, success_func
):
    half_open_breaker.call(success_func)
    assert half_open_breaker.state == CircuitBreakerState.HALF_OPEN
    assert half_open_breaker.success_count == 1

    with pytest.raises(IOError):
        half_open_breaker.call(error_func)

    assert half_open_breaker.state == CircuitBreakerState.OPEN
    assert half_open_breaker.success_count == 0


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


@pytest.mark.parametrize(
    "error_val, expected_state",
    [
        (False, CircuitBreakerState.OPEN),
        (True, CircuitBreakerState.CLOSED),
    ],
)
def test_can_detect_errors_that_are_not_exceptions(error_val, expected_state):
    breaker = CircuitBreaker(
        detect_error=lambda ret_val: ret_val is False,
        error_threshold=1,
    )

    def return_code_error():
        return error_val

    result = breaker.call(return_code_error)
    assert result is error_val
    assert breaker.state is expected_state


def test_notifies_on_breaker_open(error_func, io_error):
    mock_open = mock.Mock()
    breaker = CircuitBreaker(error_threshold=1, on_open=mock_open)

    assert mock_open.call_count == 0

    with pytest.raises(IOError):
        breaker.call(error_func)

    mock_open.assert_called_once()
    mock_open.assert_called_with(breaker, io_error)


def test_notifies_on_breaker_close(error_func, success_func):
    mock_close = mock.Mock()
    breaker = CircuitBreaker(
        error_threshold=1,
        on_close=mock_close,
        recovery_timeout=1,
    )

    assert mock_close.call_count == 0

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert mock_close.call_count == 0

    sleep(1)
    breaker.call(success_func)

    assert mock_close.call_count == 1


def test_calling_an_open_breaker_raises_an_error(error_func):
    breaker = CircuitBreaker(
        error_threshold=1, recovery_timeout=1, recovery_threshold=2
    )

    with pytest.raises(IOError):
        breaker.call(error_func)

    with pytest.raises(CircuitBreakerException):
        breaker.call(error_func)


def test_unknown_strategy_causes_error():
    with pytest.raises(ValueError):
        CircuitBreaker(strategy="foo")

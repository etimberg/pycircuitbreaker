from time import sleep

import pytest

from pycircuitbreaker import CircuitBreaker, CircuitBreakerState
from pycircuitbreaker.strategies import CircuitBreakerStrategy


def test_net_error_strategy(error_func, success_func):
    breaker = CircuitBreaker(
        strategy=CircuitBreakerStrategy.NET_ERROR,
        error_threshold=3,
    )

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.CLOSED

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.CLOSED

    breaker.call(success_func)

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.CLOSED

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN


def test_net_error_strategy_half_open_to_closed(error_func, success_func):
    breaker = CircuitBreaker(
        strategy=CircuitBreakerStrategy.NET_ERROR,
        error_threshold=1,
        recovery_timeout=1,
    )

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN

    sleep(1)
    assert breaker.state == CircuitBreakerState.HALF_OPEN

    breaker.call(success_func)
    assert breaker.state == CircuitBreakerState.CLOSED


def test_net_error_strategy_half_open_to_open(error_func, success_func):
    breaker = CircuitBreaker(
        strategy=CircuitBreakerStrategy.NET_ERROR,
        error_threshold=1,
        recovery_timeout=1,
    )

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN

    sleep(1)
    assert breaker.state == CircuitBreakerState.HALF_OPEN

    with pytest.raises(IOError):
        breaker.call(error_func)

    assert breaker.state == CircuitBreakerState.OPEN


def test_net_error_strategy_count_never_negative(success_func):
    breaker = CircuitBreaker(
        strategy=CircuitBreakerStrategy.NET_ERROR,
    )
    breaker.call(success_func)

    assert breaker._strategy._net_error_count == 0

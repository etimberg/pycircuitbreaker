from pycircuitbreaker import CircuitBreaker, CircuitBreakerException


def test_circuit_breaker_exception_serialization():
    breaker = CircuitBreaker(breaker_id="FOO")
    exception = CircuitBreakerException(breaker)
    exception_str = str(exception)
    assert "Circuit FOO OPEN until" in exception_str

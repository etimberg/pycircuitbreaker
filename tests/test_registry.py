from pycircuitbreaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerRegistryException,
)

import pytest


def test_register_new_circuit_breaker():
    registry = CircuitBreakerRegistry()
    circuit_breaker = CircuitBreaker()

    registry.register(circuit_breaker)

    registered = registry.get_circuits()
    assert len(registered) == 1
    assert registered[0] == circuit_breaker


def test_register_existing_circuit_breaker():
    registry = CircuitBreakerRegistry()
    circuit_breaker = CircuitBreaker()

    registry.register(circuit_breaker)

    with pytest.raises(CircuitBreakerRegistryException):
        registry.register(circuit_breaker)

    registered = registry.get_circuits()
    assert len(registered) == 1
    assert registered[0] == circuit_breaker


def test_get_circuits_not_empty():
    registry = CircuitBreakerRegistry()
    db_circuit = CircuitBreaker(breaker_id="db")
    service_circuit = CircuitBreaker(breaker_id="service")

    registry.register(db_circuit)
    registry.register(service_circuit)

    registered = registry.get_circuits()
    assert len(registered) == 2
    assert db_circuit in registered
    assert service_circuit in registered


def test_get_circuits_empty():
    registry = CircuitBreakerRegistry()

    registered = registry.get_circuits()

    assert len(registered) == 0


def test_get_open_circuits_empty():
    registry = CircuitBreakerRegistry()

    opened = registry.get_open_circuits()

    assert len(opened) == 0


def test_get_open_circuits_when_all_circuits_are_closed():
    registry = CircuitBreakerRegistry()
    circuit = CircuitBreaker(breaker_id="closed_breaker", error_threshold=1)
    registry.register(circuit)

    opened = registry.get_open_circuits()

    assert len(opened) == 0


def test_get_open_circuits_when_one_circuit_is_open(error_func):
    registry = CircuitBreakerRegistry()
    open_circuit = CircuitBreaker(breaker_id="open_breaker", error_threshold=1)
    closed_circuit = CircuitBreaker(breaker_id="closed_breaker")
    registry.register(open_circuit)
    registry.register(closed_circuit)

    with pytest.raises(IOError):
        open_circuit.call(error_func)

    opened = registry.get_open_circuits()

    assert len(opened) == 1
    assert open_circuit in opened
    assert closed_circuit not in opened

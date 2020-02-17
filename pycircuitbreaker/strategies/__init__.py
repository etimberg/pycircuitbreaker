from enum import Enum

from .single_reset import SingleResetStrategy


class CircuitBreakerStrategy(Enum):
    SINGLE_RESET = "SINGLE_RESET"


def get_strategy(strategy: CircuitBreakerStrategy):
    if strategy == CircuitBreakerStrategy.SINGLE_RESET:
        return SingleResetStrategy

    raise ValueError(f"Unknown circuit breaker strategy {strategy}")

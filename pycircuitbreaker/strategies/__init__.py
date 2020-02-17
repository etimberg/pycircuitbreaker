from enum import Enum

from .net_error import NetErrorStrategy
from .single_reset import SingleResetStrategy


class CircuitBreakerStrategy(Enum):
    SINGLE_RESET = "SINGLE_RESET"
    NET_ERROR = "NET_ERROR"


def get_strategy(strategy: CircuitBreakerStrategy):
    if strategy == CircuitBreakerStrategy.SINGLE_RESET:
        return SingleResetStrategy
    elif strategy == CircuitBreakerStrategy.NET_ERROR:
        return NetErrorStrategy

    raise ValueError(f"Unknown circuit breaker strategy {strategy}")

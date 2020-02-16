from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache, wraps
from typing import Callable, Iterable, Optional
from uuid import uuid4


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    HALF_OPEN = "HALF_OPEN"
    OPEN = "OPEN"


@lru_cache()
def exception_in_list(exception: Exception, type_list: Iterable[Exception]):
    """
    Check if the exception matches any type in the list considering derived types

    This was extracted from the CircuitBreaker class to enable use of the lru_cache
    """
    return any(isinstance(exception, exc_type) for exc_type in type_list)


class CircuitBreaker:
    ERROR_THRESHOLD = 5
    RECOVERY_THRESHOLD = 1
    RECOVERY_TIMEOUT = 30

    def __init__(
        self,
        breaker_id: Optional = None,
        exception_blacklist: Optional[Iterable[Exception]] = None,
        exception_whitelist: Optional[Iterable[Exception]] = None,
        error_threshold: int = ERROR_THRESHOLD,
        recovery_threshold: int = RECOVERY_THRESHOLD,
        recovery_timeout: int = RECOVERY_TIMEOUT,
    ):
        self._id = breaker_id or uuid4()
        self._error_count = 0
        self._error_threshold = error_threshold
        self._exception_blacklist = frozenset(exception_blacklist or [])
        self._exception_whitelist = frozenset(exception_whitelist or [])
        self._recovery_threshold = recovery_threshold
        self._recovery_timeout = recovery_timeout
        self._state = CircuitBreakerState.CLOSED
        self._success_count = 0
        self._time_opened = datetime.utcnow()

    def call(self, func, *args, **kwargs):
        """
        Call the supplied function respecting the circuit breaker rule
        """
        if self.state == CircuitBreakerState.OPEN:
            # TODO: replace this with a configurable error
            raise Exception("CIRCUIT BREAKER IS OPEN")

        try:
            func(*args, *kwargs)
        except Exception as ex:
            if not self._exception_whitelisted(ex) and self._exception_blacklisted(ex):
                self._handle_error()
                raise

        self._handle_success()

    def _exception_blacklisted(self, exception):
        """
        Determine if an exception type is blacklisted by checking to see
        if it matches any type in the blacklist
        """
        if (
            not self._exception_blacklist
            or type(exception) in self._exception_blacklist
        ):
            return True

        return exception_in_list(exception, self._exception_blacklist)

    def _exception_whitelisted(self, exception):
        """
        Determine if an exception type is whitelisted by checking to see
        if it matches any type in the whitelist
        """
        if type(exception) in self._exception_whitelist:
            return True

        return exception_in_list(exception, self._exception_whitelist)

    def _handle_error(self):
        self._error_count += 1

        if self._error_count >= self._error_threshold:
            self._state = CircuitBreakerState.OPEN
            self._success_count = 0
            self._time_opened = datetime.utcnow()

    def _handle_success(self):
        self._success_count += 1

        if self._success_count >= self._recovery_threshold:
            self._state = CircuitBreakerState.CLOSED
            self._error_count = 0

    @property
    def state(self) -> CircuitBreakerState:
        """
        The state of the breaker.
        If the breaker is open but enough time (defined by the recovery_time setting)
        has elapsed, the breaker is moved to the half_open state
        """
        if (
            self._state == CircuitBreakerState.OPEN
            and datetime.utcnow() >= self.recovery_start_time
        ):
            return CircuitBreakerState.HALF_OPEN
        return self._state

    @property
    def recovery_start_time(self) -> datetime:
        """
        The UTC time until which the breaker is fully open. After this time,
        the recovery period will begin and test requests will be allowed through
        """
        return self._time_opened + timedelta(seconds=self._recovery_timeout)


def circuit(func: Callable, **kwargs) -> Callable:
    """
    Decorates the supplied function with the circuit breaker pattern.
    """
    if not callable(func):
        raise ValueError(
            f"Circuit breakers can only wrap somthing that is callable. Attempted to wrap {func}"
        )

    breaker = CircuitBreaker(**kwargs)

    @wraps(func)
    def circuit_wrapper(*args, **kwargs):
        return breaker.call(func, *args, **kwargs)

    return circuit_wrapper

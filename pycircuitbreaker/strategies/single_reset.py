from datetime import datetime

from ..state import CircuitBreakerState


class SingleResetStrategy:
    def __init__(self, error_threshold, recovery_threshold):
        self._error_count = 0
        self._error_threshold = error_threshold
        self._recovery_threshold = recovery_threshold
        self._success_count = 0
        self._state = CircuitBreakerState.CLOSED

    def handle_error(self) -> bool:
        self._error_count += 1
        opened = False

        if self._error_count >= self._error_threshold:
            self._state = CircuitBreakerState.OPEN
            self._success_count = 0
            opened = True

        return opened

    def handle_success(self) -> bool:
        self._success_count += 1
        closed = False

        if self._success_count >= self._recovery_threshold:
            self._state = CircuitBreakerState.CLOSED
            self._error_count = 0
            closed = True

        return closed

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def state(self) -> CircuitBreakerState:
        return self._state

    @property
    def success_count(self) -> int:
        return self._success_count

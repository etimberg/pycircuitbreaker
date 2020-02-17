from datetime import datetime

from ..state import CircuitBreakerState


class NetErrorStrategy:
    def __init__(self, error_threshold, recovery_threshold):
        self._error_threshold = error_threshold
        self._net_error_count = 0
        self._recovery_threshold = recovery_threshold
        self._state = CircuitBreakerState.CLOSED

    def handle_error(self) -> bool:
        self._net_error_count += 1
        opened = False

        if self._net_error_count >= self._error_threshold:
            self._state = CircuitBreakerState.OPEN
            opened = True

        return opened

    def handle_success(self) -> bool:
        self._net_error_count = max(0, self._net_error_count - 1)
        closed = False

        if self._net_error_count < self._error_threshold:
            self._state = CircuitBreakerState.CLOSED
            closed = True

        return closed

    @property
    def error_count(self) -> int:
        return max(0, self._net_error_count - self._error_threshold)

    @property
    def state(self) -> CircuitBreakerState:
        return self._state

    @property
    def success_count(self) -> int:
        return max(0, self._error_threshold - self._net_error_count)

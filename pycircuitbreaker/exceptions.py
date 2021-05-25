from datetime import datetime


class CircuitBreakerException(Exception):
    def __init__(self, breaker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._breaker = breaker

    def __str__(self):
        seconds_remaining = (
            self._breaker.recovery_start_time - datetime.utcnow()
        ).total_seconds()
        return (
            f"Circuit {self._breaker.id} OPEN "
            f"until {self._breaker.recovery_start_time.isoformat()} "
            f"({self._breaker.error_count} errors, {seconds_remaining} sec remaining)"
        )


class CircuitBreakerRegistryException(Exception):
    pass

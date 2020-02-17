# PyCircuitBreaker

[![PyPI Version](https://img.shields.io/pypi/v/pycircuitbreaker)](https://pypi.org/project/pycircuitbreaker/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pycircuitbreaker)](https://pypi.org/project/pycircuitbreaker/)
[![MIT License](https://img.shields.io/pypi/l/pycircuitbreaker)](https://github.com/etimberg/pycircuitbreaker/blob/master/LICENSE)
![CI Status](https://img.shields.io/github/workflow/status/etimberg/pycircuitbreaker/CI)
[![Coverage Status](https://coveralls.io/repos/github/etimberg/pycircuitbreaker/badge.svg?branch=master)](https://coveralls.io/github/etimberg/pycircuitbreaker?branch=master)

Python Implementation of the [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html). Inspired by [circuitbreaker](https://github.com/fabfuel/circuitbreaker) by Fabian Fuelling.

## Installation

```
pip install pycircuitbreaker
```

## Usage

The simplest usage of `pycircuitbreaker` is to wrap decorate a function that can fail using `circuit`.

```python
from pycircuitbreaker import circuit

@circuit
def function_that_can_fail():
    ...
```

### Reset Strategies

By default, pycircuitbreaker operates such that a single success resets the error state of a closed breaker. This makes sense for a service that rarely fails, but in certains cases this can pose a problem. If the `error_threshold` is set to `5`, but only 4/5 external requests fail, the breaker will never open. To get around this, the [strategy setting])(#strategy) may be used. By setting this to `pycircuitbreaker.CircuitBreakerStrategy.NET_ERROR`, the net error count (errors - successes) will be used to trigger the breaker.

## Configuration

A number of configuration options can be provided to the `CircuitBreaker` class or the `circuit` decorator to control the behaviour of the breaker. When using the decorator, options should be passed as keyword arguments.

### breaker_id

The ID of the breaker used in exception reporting or for logging purposes. If not specified, a `uuid4()` is created.

### detect_error

Type: `Optional[Callable[Any, bool]]`

This option can be used to detect errors that do not raise exceptions. For example, if you have a function that returns a response object with a status code, we can detect errors that have a status code of 500.

```python
from pycircuitbreaker import circuit

def detect_500(response) -> bool:
    return response.status_code == 500

@circuit(detect_error=detect_500)
def request():
    response = external_call()
    return response
```

### error_threshold

Type: `Optional[int]`
Default: `5`

The number of sequential errors that must occur before the breaker opens. If 4 errors occur a single success will reset the error count to 0.

### exception_blacklist

Type: `Optional[Iterable[Exception]]`

There are cases where only certain errors should count as errors that can open the breaker. In the example below, we are using [requests](https://requests.readthedocs.io/en/master/) to call to an external service and then raise an exception on an error case. We only want the circuit breaker to open on timeouts to
the external service. 

Note that if this option is used, errors derived from those specified will also be included in the blacklist.

```python
import requests
from pycircuitbreaker import circuit

@circuit(exception_blacklist=[requests.exceptions.Timeout])
def external_call():
    response = requests.get("EXTERNAL_SERVICE")
    response.raise_for_status()
```

### exception_whitelist

Type: `Optional[Iterable[Exception]]`

This setting allows certain exceptions to not be counted as errors. Taking the same example as the exception_blacklist setting, we can ignore `request.exceptions.HTTPError` only using the whitelist.

Note that if this option is used, errors derived from those specified will also be included in the whitelist.

```python
import requests
from pycircuitbreaker import circuit

@circuit(exception_whitelist=[requests.exceptions.HTTPError])
def external_call():
    response = requests.get("EXTERNAL_SERVICE")
    response.raise_for_status()
```

### on_close

Type: `Optional[Callable[[CircuitBreaker], None]]`

If specified, this function is called when the breaker fully closes. This can be useful for logging messages.

### on_open

Type: `Optional[Callable[[CircuitBreaker, Union[Exception, Any]], None]]`

If specified, this function is called when the breaker opens. The 2nd parameter to the function will be the exception that triggered the opening if exception detection was used. If the `detect_error` method was used, the wrapped function return value is passed as the 2nd parameter.

### recovery_threshold

Type: `Optional[int]`
Default: `1`

This is the number of successful calls that must occur before the circuit breaker transitions from `CircuitBreakerState.HALF_OPEN` to `CircuitBreakerState.CLOSED`.

### recovery_timeout

Type: `Optional[int]`
Default: 30

The number of seconds the breaker stays fully open for before test requests are allowed through.

### strategy

Type: `Optional[pycircuitbreaker.CircuitBreakerStrategy]`
Default: `pycircuitbreaker.CircuitBreakerStrategy.SINGLE_RESET`

Controls how successes change the error count when the breaker is closed. By default, a single success resets the number of errors in the breaker.

Possible options:
* `CircuitBreakerStrategy.SINGLE_RESET`
* `CircuitBreakerStrategy.NET_ERROR`

## CircuitBreaker API

The public API of the `CircuitBreaker` class is described below.

### error_count

Type: `int`

The number of errors stored in the breaker.

### id

The ID of the breaker. If not supplied via the configuration `breaker_id` setting, this is a `uuid4()`.

### open_time

Type: `datetime`

The UTC time the breaker last opened.

### recovery_start_time

Type: `datetime`

The UTC time that the breaker is open until (when recovery begins).

### state

Type: `CircuitBreakerState`

The state of the breaker.

### success_count

Type: `int`

The number of successes stored in the breaker during the recovery period.

## Roadmap

1. Back circuit breaker state with Redis to share state among processes (e.g. for gunicorn)
import pytest

from pycircuitbreaker import circuit, CircuitBreakerException


def test_decorator_raises_error_if_no_callable_passed():
    with pytest.raises(ValueError):
        circuit("not a function")


def test_decorator_success(success_func):
    wrapped = circuit(success_func)
    assert wrapped() == True


def test_decorator_error(error_func):
    wrapped = circuit(error_func, error_threshold=1)

    with pytest.raises(IOError):
        wrapped()
    
    with pytest.raises(CircuitBreakerException):
        wrapped()


def test_decorator_passes_args_to_wrapped_function():
    def func(arg):
        return arg

    wrapped = circuit(func)
    assert wrapped('foo') == 'foo'

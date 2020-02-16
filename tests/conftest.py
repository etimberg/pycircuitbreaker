import pytest


@pytest.fixture()
def io_error():
    return IOError()


@pytest.fixture()
def error_func(io_error):
    def raises_error():
        raise io_error

    return raises_error


@pytest.fixture()
def success_func():
    def success():
        return True

    return success

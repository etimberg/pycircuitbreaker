import pytest


@pytest.fixture()
def error_func():
    def raises_error():
        raise IOError

    return raises_error


@pytest.fixture()
def success_func():
    def success():
        return True

    return success

import pytest

from migration_lambda.error_on_lambda_timeout import LambdaTimeoutException, timeout_handler


def test__timeout_handler__raises__exception():
    with pytest.raises(LambdaTimeoutException):
        timeout_handler(None, None)

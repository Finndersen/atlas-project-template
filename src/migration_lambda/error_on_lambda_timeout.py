import math
import signal
from collections.abc import Callable
from types import FrameType
from typing import Any

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext


class LambdaTimeoutException(Exception):
    pass


def timeout_handler(_signal: int, _frame: FrameType | None) -> None:
    raise LambdaTimeoutException("Lambda time limit exceeded")


signal.signal(signal.SIGALRM, timeout_handler)


@lambda_handler_decorator
def error_on_timeout(handler: Callable, event: Any, context: LambdaContext, **kwargs: Any) -> None:
    try:
        remaining = context.get_remaining_time_in_millis()
        remaining_seconds = math.floor(remaining / 1000)

        signal.alarm(remaining_seconds - 1)

        return handler(event, context, **kwargs)
    finally:
        signal.alarm(0)

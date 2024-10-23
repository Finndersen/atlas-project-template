from dataclasses import dataclass
from unittest import mock

import pytest
from aws_embedded_metrics.logger.metrics_logger_factory import create_metrics_logger


@pytest.fixture
def lambda_context():
    """
    https://docs.powertools.aws.dev/lambda/python/latest/core/logger/#testing-your-code
    """

    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

        @staticmethod
        def get_remaining_time_in_millis() -> int:
            return 0

    yield LambdaContext()


@pytest.fixture  # type: ignore
def local_metrics_logger():
    """
    Should be used with the following env setup:
    AWS_EMF_DISABLE_METRIC_EXTRACTION=true
    AWS_EMF_ENVIRONMENT=local
    """
    logger = create_metrics_logger()

    yield logger

    logger.flush()


@pytest.fixture
def mock_db_auth_token():
    with mock.patch("boto3.client") as mock_boto_client:
        mock_boto_client.return_value.generate_db_auth_token.return_value = "mypassword"
        yield mock_boto_client

import os
from dataclasses import dataclass

import boto3  # type: ignore
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from aws_embedded_metrics.metric_scope import metric_scope
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from migration_lambda.apply import DBConfig, apply_migrations
from migration_lambda.cfn_response import RequestType, ResponseStatus, send_response
from migration_lambda.error_on_lambda_timeout import error_on_timeout
from migration_lambda.verify_migrations import verify_migration_hash


@dataclass
class RunResult:
    status: ResponseStatus
    reason: str


def run(event: APIGatewayProxyEvent, metrics: MetricsLogger) -> RunResult:
    # Only run migrations on Create or Update event
    if event["RequestType"] in {RequestType.CREATE.value, RequestType.UPDATE.value}:
        verify_migration_hash(event)
        migration_result = apply_migrations(db_config=get_db_config())
        if migration_result.returncode != 0:
            result = RunResult(status=ResponseStatus.FAILED, reason=f"Migration failed: {migration_result.stderr}")
        else:
            result = RunResult(status=ResponseStatus.SUCCESS, reason="Migration successfully applied")
            metrics.set_property("migrationResult", migration_result.stdout)
    else:
        result = RunResult(status=ResponseStatus.SUCCESS, reason="Migration not required for Delete event")

    return result


def get_db_config():
    """
    Read DB config params from environment variables.
    Get an auth token password from the RDS proxy (using IAM authentication)
    :return:
    """
    host = os.environ["DB_HOST"]
    port = int(os.environ["DB_PORT"])
    user = os.environ["DB_USER"]
    name = os.environ["DB_NAME"]
    rds_client = boto3.client("rds")
    password = rds_client.generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=user,
    )
    return DBConfig(host=host, port=port, name=name, user=user, password=password)


@error_on_timeout
@metric_scope
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext, metrics: MetricsLogger):
    """
    Lambda handler function for the Custom Resource
    Request fields provided in event are documented here:
    https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requests.html
    """
    # Initialise result with a default value to please type checkers, but this should always be overridden
    result: RunResult = RunResult(status=ResponseStatus.FAILED, reason="Result not set")
    try:
        metrics.set_property("requestType", event["RequestType"])  # Create | Update | Delete
        metrics.set_property("ResponseURL", event["ResponseURL"])  # URL where response should be sent to
        result = run(event, metrics)
    except Exception as e:
        # Want to make sure response is sent even if an exception occurs, otherwise CloudFormation will be left hanging
        result = RunResult(
            status=ResponseStatus.FAILED,
            reason=f"Exception occurred during Lambda execution: {type(e).__name__}: {str(e)}",
        )
    finally:
        metrics.set_property("outcome", f"{result.status}: {result.reason}")
        send_response(event, result.status, data={"result": result.reason}, reason=result.reason)

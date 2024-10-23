import json
from unittest import mock

from aws_embedded_metrics import MetricsLogger
from aws_lambda_powertools.utilities.typing import LambdaContext

from migration_lambda.aws import lambda_handler
from migration_lambda.verify_migrations import get_atlas_hash_value
from tests.migration_lambda.util import build_cfn_event


@mock.patch("subprocess.run")
@mock.patch("requests.put")
def test__lambda_handler__runs_migrations_and_sends_appropriate_response(
    mock_requests_put,
    mock_subprocess_run,
    mock_db_auth_token,
    lambda_context: LambdaContext,
    local_metrics_logger: MetricsLogger,
    capsys,
):
    mock_subprocess_run.return_value = mock.MagicMock(returncode=0, stdout="Success")
    event = build_cfn_event("Create", migration_hash=get_atlas_hash_value())

    lambda_handler(event=event, context=lambda_context, metrics=local_metrics_logger)

    log = capsys.readouterr().out.strip()  # remove any extra line
    metrics_output = json.loads(log)  # deserialize JSON str

    # Verify metrics logging
    assert metrics_output["requestType"] == "Create"
    assert metrics_output["ResponseURL"] == event["ResponseURL"]
    assert metrics_output["outcome"] == "SUCCESS: Migration successfully applied"
    assert metrics_output["migrationResult"] == "Success"

    # Verify migrations run
    mock_subprocess_run.assert_called_once()

    # Verify response sent
    mock_requests_put.assert_called_once()


@mock.patch("requests.put")
def test__lambda_handler__returns_failed_response__when_exception_occurs(
    mock_requests_put,
    lambda_context: LambdaContext,
    local_metrics_logger: MetricsLogger,
    capsys,
):
    event = build_cfn_event("Create", migration_hash="different_hash_value")
    lambda_handler(event=event, context=lambda_context, metrics=local_metrics_logger)

    log = capsys.readouterr().out.strip()  # remove any extra line
    metrics_output = json.loads(log)  # deserialize JSON str

    # Verify metrics logging
    assert metrics_output["requestType"] == "Create"
    assert metrics_output["ResponseURL"] == event["ResponseURL"]
    assert (
        "FAILED: Exception occurred during Lambda execution: MigrationHashMismatchError: " in metrics_output["outcome"]
    )

    # Verify response sent
    mock_requests_put.assert_called_once()

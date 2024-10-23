from unittest import mock

import pytest

from migration_lambda.aws import run
from migration_lambda.cfn_response import ResponseStatus
from tests.migration_lambda.util import build_cfn_event


@mock.patch("migration_lambda.aws.apply_migrations")
@mock.patch("migration_lambda.aws.verify_migration_hash")
@pytest.mark.parametrize("event_type", ["Create", "Update"])
def test__run__create_update_event__apply_fail__returns_failed_response(
    mock_verify_migration_hash: mock.MagicMock,
    mock_apply_migrations: mock.MagicMock,
    mock_db_auth_token,
    event_type: str,
):
    mock_apply_migrations.return_value = mock.MagicMock(returncode=1, stderr="Error")
    event = build_cfn_event(event_type)
    metrics_logger = mock.MagicMock()
    result = run(event, metrics_logger)
    mock_verify_migration_hash.assert_called_once()
    assert result.status == ResponseStatus.FAILED
    assert "Migration failed: Error" in result.reason


@mock.patch("migration_lambda.aws.apply_migrations")
@mock.patch("migration_lambda.aws.verify_migration_hash")
@pytest.mark.parametrize("event_type", ["Create", "Update"])
def test__run__create_update_event__apply_succeed__returns_success_response(
    mock_verify_migration_hash: mock.MagicMock,
    mock_apply_migrations: mock.MagicMock,
    mock_db_auth_token,
    event_type: str,
):
    mock_apply_migrations.return_value = mock.MagicMock(returncode=0, stdout="1 Migration applied")
    event = build_cfn_event(event_type)
    metrics_logger = mock.MagicMock()
    result = run(event, metrics_logger)
    metrics_logger.set_property.assert_called_once()
    mock_verify_migration_hash.assert_called_once()
    assert result.status == ResponseStatus.SUCCESS
    assert "Migration successfully applied" in result.reason


def test__run__delete_event__returns_success_response():
    event = build_cfn_event("Delete")
    metrics_logger = mock.MagicMock()
    result = run(event, metrics_logger)
    assert result.status == ResponseStatus.SUCCESS
    assert "Migration not required for Delete event" in result.reason

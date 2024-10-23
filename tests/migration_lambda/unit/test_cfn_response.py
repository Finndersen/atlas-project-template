from unittest import mock

import pytest

from migration_lambda.cfn_response import ResponseStatus, _rand_string, send_response
from tests.migration_lambda.util import build_cfn_event


@mock.patch("requests.put")
@mock.patch("migration_lambda.cfn_response._rand_string")
def test__send_response__for_create_request(mock_rand_string, mock_requests_put):
    mock_rand_string.return_value = "12345678"
    event = build_cfn_event("Create")
    send_response(
        event=event, status=ResponseStatus.SUCCESS, data={"result": "Migrate success"}, reason="Migrations applied"
    )
    mock_requests_put.assert_called_with(
        "https://response-url.s3.aws.com",
        json={
            "Status": "SUCCESS",
            "Reason": "Migrations applied",
            "PhysicalResourceId": "StackId_CustomResourceLogicalID_12345678",
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"],
            "NoEcho": False,
            "Data": {"result": "Migrate success"},
        },
        timeout=10,
    )


@mock.patch("requests.put")
@pytest.mark.parametrize("request_type", ["Delete", "Update"])
def test__send_response__for_update_delete_request(mock_requests_put, request_type):
    event = build_cfn_event(request_type)
    send_response(
        event=event, status=ResponseStatus.SUCCESS, data={"result": "Migrate success"}, reason="Migrations applied"
    )
    mock_requests_put.assert_called_with(
        "https://response-url.s3.aws.com",
        json={
            "Status": "SUCCESS",
            "Reason": "Migrations applied",
            "PhysicalResourceId": "CR-PhysicalId-123",
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"],
            "NoEcho": False,
            "Data": {"result": "Migrate success"},
        },
        timeout=10,
    )


def test__rand_string():
    result = _rand_string(10)
    assert len(result) == 10
    assert isinstance(result, str)

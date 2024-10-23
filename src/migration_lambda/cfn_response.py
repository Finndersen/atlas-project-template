import random
import string
from enum import StrEnum
from typing import Any

import requests
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent


class ResponseStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class RequestType(StrEnum):
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"


def send_response(
    event: APIGatewayProxyEvent,
    status: ResponseStatus,
    data: dict[str, Any] | None = None,
    no_echo: bool = False,
    reason: str = "",
) -> requests.Response:
    """
    Sends the confirmation response of a custom-resource triggered Lambda function back to CloudFormation
    :param event: The event object passed to the Lambda function
    :param context: The context object passed to the Lambda function
    :param status: The status of the response, either "SUCCESS" or "FAILED"
    :param data: The custom resource provider-defined name-value pairs to send with the response.
        You can access the values provided here by name in the template with Fn::GetAtt
    :param no_echo: Indicates whether to mask the output of the custom resource when it's retrieved by using the
        Fn::GetAtt function.
    :param reason: Describes the reason for a failure response.
    """
    if event["RequestType"] == RequestType.CREATE.value:
        # For Create requests, need to generate a new unique physicalResourceId
        physical_resource_id = "_".join([event["StackId"].split("/")[1], event["LogicalResourceId"], _rand_string(8)])
    else:
        # PhysicalResourceId should always be provided with Update and Delete requests
        physical_resource_id = event["PhysicalResourceId"]

    response_body = {
        "Status": status,
        "Reason": reason,
        "PhysicalResourceId": physical_resource_id,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "NoEcho": no_echo,
        "Data": data or {},
    }
    response_url = event["ResponseURL"]

    return requests.put(response_url, json=response_body, timeout=10)


def _rand_string(str_len: int) -> str:
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(str_len))

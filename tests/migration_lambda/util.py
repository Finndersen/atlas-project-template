import json

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

ALLOWED_MASTER_PRINCIPAL = {
    "urn": "urn:ves:auth:user:/upside/people/joe.bloggs",
    "username": "joe.bloggs",
    "statements": [
        {
            "effect": "ALLOW",
            "actions": [
                "*",
            ],
            "resources": [
                "**/*",
            ],
        }
    ],
}


def build_cfn_event(
    request_type, migration_hash="8pcVvFd0fQpYQOuXnf+i5X2SkwHuFioIt7pxntk6Twg="
) -> APIGatewayProxyEvent:
    event = {
        "RequestType": request_type,
        "LogicalResourceId": "CustomResourceLogicalID",
        "StackId": "FM-DB/StackId",
        "RequestId": "123456",
        "ResponseURL": "https://response-url.s3.aws.com",
        "requestContext": {
            "authorizer": {
                "principal": json.dumps(ALLOWED_MASTER_PRINCIPAL),
                "authorizationToken": "authorization token from authorizer",
            }
        },
        "ResourceProperties": {"MigrationHash": migration_hash},
    }
    if request_type != "Create":
        event["PhysicalResourceId"] = "CR-PhysicalId-123"
    return APIGatewayProxyEvent(event)

import time
from dataclasses import dataclass
from unittest import mock

import pytest
from aws_embedded_metrics.logger.metrics_logger_factory import create_metrics_logger
from pytest import fixture
from sqlalchemy import Connection, create_engine
from sqlalchemy.exc import OperationalError
from testcontainers.postgres import PostgresContainer

from db.models import Base
from db.session import DBSessionMaker


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


@fixture(scope="session")
def postgresql_db_container() -> PostgresContainer:
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@fixture(scope="session")
def db_connection(postgresql_db_container: PostgresContainer) -> Connection:
    """
    Fixture to provide a SQLAlchemy connection for the containerised database.
    This connection is re-used for the entire test session.
    """
    connection_url = postgresql_db_container.get_connection_url()
    engine = create_engine(connection_url)

    retries = 5
    while True:
        try:
            with engine.connect() as connection:
                yield connection
            break
        except OperationalError:
            print("Container connection failed, retrying...")
            # Occasionally the container port forwarding isn't ready yet, so wait some time and retry
            # (colima issue, see https://github.com/abiosoft/colima/issues/71)
            retries -= 1
            if retries == 0:
                raise
            time.sleep(1)


@fixture(scope="session")
def db_tables(db_connection):
    """
    Fixture to create all the tables in the database.
    Dropping tables afterwards should not be necessary since the entire container will be cleared
    """
    with db_connection.begin():
        Base.metadata.create_all(db_connection)
    yield


@fixture()
def db_session_maker(db_connection: Connection, db_tables) -> DBSessionMaker:
    """
    Provides a SQLAlchemy DB session for each test
    (within a transaction, so changes will be rolled back after each test).
    Also patches the Dippy-registered DBSession with this test session.
    """
    # If using requests_mock, can disable it for localhost container requests like:
    # requests_mock.register_uri(requests_mock_lib.ANY, re.compile("localhost/"), real_http=True)
    with db_connection.begin() as transaction:
        # Set join_transaction_mode so that subsequent nested transactions are implemented as savepoints,
        # so that this outer transaction does not become broken during a rollback.
        session_maker = DBSessionMaker(bind=db_connection, join_transaction_mode="create_savepoint")
        yield session_maker
        # Rollback transaction so that each test is isolated
        transaction.rollback()

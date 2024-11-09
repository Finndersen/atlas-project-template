import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import InvalidRequestError

from db.models import User
from db.session import DBSessionMaker
from tests.data import get_user


@pytest.mark.parametrize("exec_count", range(2))
def test__transaction_isolation__between_tests(exec_count, db_session_maker: DBSessionMaker):
    """
    Verify that database state is reset between tests
    """
    with db_session_maker.begin() as session:
        # Verify no data
        user_count = session.execute(select(func.count(User.id))).scalar()
        assert user_count == 0
        session.add(get_user())
        user_count = session.execute(select(func.count(User.id))).scalar()
        assert user_count == 1


def test__transaction_rollback__when_exception(db_session_maker: DBSessionMaker):
    """
    Verify that a transaction is rolled back if it exits due to an exception
    """
    try:
        with db_session_maker.begin() as session:
            session.add(get_user())
            user_count = session.execute(select(func.count(User.id))).scalar()
            assert user_count == 1
            raise Exception("Rollback")
    except Exception:
        with db_session_maker.begin() as session:
            user_count = session.execute(select(func.count(User.id))).scalar()
            assert user_count == 0


def test__transaction_persisted(db_session_maker: DBSessionMaker):
    """
    Verify that writes in a transaction are persisted, and visible from another transaction
    """
    with db_session_maker.begin() as session:
        user_count = session.execute(select(func.count(User.id))).scalar()
        assert user_count == 0
        session.add(get_user())

    with db_session_maker.begin() as session:
        user_count = session.execute(select(func.count(User.id))).scalar()
        assert user_count == 1


def test__cannot_implicitly_begin_transaction(db_session_maker: DBSessionMaker):
    """
    Verify that a session cannot be used without explicitly starting a transaction
    """
    session = db_session_maker()
    with pytest.raises(InvalidRequestError):
        session.add(get_user())

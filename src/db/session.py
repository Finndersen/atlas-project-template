import contextlib
from typing import Any

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.session import _SessionBind


class DBSessionMaker:
    """
    Wrapper around sessionmaker[Session] to support type hinting and enabling its registration as a service as
    service registration does not support generics.

    Should always be used as a context manager to ensure transactions are explicitly opened and closed, e.g:

    # Module / global scope
    engine = create_engine(<DB_CONNECTION_STR>)
    db_session_maker = DBSessionMaker(bind=engine)

    # Function / request scope
    with db_session_maker.begin() as session:
        session.add(my_object)
    """

    def __init__(self, bind: _SessionBind, **kwargs: Any):
        # Set autobegin=False so the session must always be used as a context manager to explicitly open a transaction
        self._sessionmaker = sessionmaker(bind, autobegin=False, **kwargs)

    def __call__(self) -> Session:
        """
        Create a new session instance with the configured bind.
        """
        return self._sessionmaker()

    def begin(self) -> contextlib.AbstractContextManager[Session]:
        """
        Used as a context manager, initialises a new session and begins a transaction
        """
        return self._sessionmaker.begin()

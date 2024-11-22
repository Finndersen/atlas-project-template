from db.models import User


def get_user() -> User:
    """
    Create a test user instance
    """
    return User(name="John Smith", email="john.smith@gmail.com")

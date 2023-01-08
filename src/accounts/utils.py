from uuid import uuid4


def uuid():
    """
    Generate a new UUID.
    """
    return uuid4().hex

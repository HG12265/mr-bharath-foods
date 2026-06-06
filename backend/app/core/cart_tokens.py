import uuid


def generate_guest_token() -> str:
    """
    Generates a secure UUID4 guest token.
    """
    return str(uuid.uuid4())

def is_valid_guest_token(token: str) -> bool:
    """
    Validates if the given token is a valid UUID4 string.
    """
    try:
        uuid.UUID(token, version=4)
        return True
    except ValueError:
        return False

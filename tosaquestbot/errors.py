class TokenAlreadyExistsError(Exception):
    """Raised when a user tries to create a token that already exists."""


class TokenAlreadyActivatedError(Exception):
    """Raised when a user tries to activate an already activated token."""


class TokenNotFoundError(Exception):
    """Raised when a user tries to activate/modify a token that doesn't exist."""

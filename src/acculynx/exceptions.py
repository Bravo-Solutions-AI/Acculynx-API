from typing import Optional


class AccuLynxAPIError(Exception):
    """Base exception for AccuLynx API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AccuLynxAPIError):
    """Raised when authentication fails."""
    pass


class NotFoundError(AccuLynxAPIError):
    """Raised when a requested resource is not found."""
    pass


class ValidationError(AccuLynxAPIError):
    """Raised when request validation fails."""
    pass


class RateLimitError(AccuLynxAPIError):
    """Raised when API rate limit is exceeded."""
    pass 
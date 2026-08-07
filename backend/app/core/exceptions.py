class AgileGraphException(Exception):
    """Base exception for the AgileGraph domain."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationException(AgileGraphException):
    """Raised when an entity fails validation."""


class ResourceNotFoundException(AgileGraphException):
    """Raised when a requested resource is not found."""


class EntityTooLargeException(AgileGraphException):
    """Raised when a payload or archive exceeds size limits."""

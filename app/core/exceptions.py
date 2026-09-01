"""
BuildOS User Service
Application Exceptions
"""


class UserServiceError(Exception):
    """Base exception for the user service."""


class UserNotFoundError(UserServiceError):
    """Raised when a user cannot be found."""


class UserAlreadyExistsError(UserServiceError):
    """Raised when attempting to create a duplicate user."""


class IdentityAlreadyExistsError(UserServiceError):
    """Raised when an identity is already taken."""


class InvalidUserStatusTransitionError(UserServiceError):
    """Raised when an invalid status transition is attempted."""


class ProfileUpdateError(UserServiceError):
    """Raised when a profile update fails validation."""


class UnauthorizedAccessError(UserServiceError):
    """Raised when a user attempts an unauthorized operation."""


class IntegrationError(UserServiceError):
    """Raised when an external service integration fails."""


class ConfigurationError(UserServiceError):
    """Raised when configuration is invalid."""

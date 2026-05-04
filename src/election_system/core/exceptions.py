class DomainError(Exception):
    """Base domain/application exception."""


class AuthError(DomainError):
    """Base auth error."""


class InvalidCredentialsError(AuthError):
    """Credentials are invalid or user is disabled."""


class ChallengeInvalidError(AuthError):
    """OTP challenge does not exist or is no longer usable."""


class ConflictError(DomainError):
    """Resource conflict (e.g. duplicate email or duplicate role assignment)."""


class DeliveryChannelUnavailableError(AuthError):
    """Requested second-factor delivery channel is not available for this user."""


class NotFoundError(DomainError):
    """Requested resource does not exist."""


class StorageError(DomainError):
    """File storage operation failed."""


class InvalidAssetError(DomainError):
    """Uploaded file is not an accepted image format or exceeds size limit."""

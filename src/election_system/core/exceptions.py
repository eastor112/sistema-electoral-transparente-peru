class DomainError(Exception):
    """Base domain/application exception."""


class AuthError(DomainError):
    """Base auth error."""


class InvalidCredentialsError(AuthError):
    """Credentials are invalid or user is disabled."""


class ChallengeInvalidError(AuthError):
    """OTP challenge does not exist or is no longer usable."""


class ConflictError(AuthError):
    """Resource conflict (e.g. duplicate email)."""


class DeliveryChannelUnavailableError(AuthError):
    """Requested second-factor delivery channel is not available for this user."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ALLOWED_JWT_ALGORITHMS = frozenset({"HS256", "HS384", "HS512"})
_INSECURE_JWT_DEFAULTS = frozenset({"replace-me", "secret", "changeme", ""})
_DEV_ENVS = frozenset({"dev", "local", "development", "test"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="election-system")
    app_env: str = Field(default="local")
    app_debug: bool = Field(default=False)
    api_v1_prefix: str = Field(default="/api/v1")

    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="election_system")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")

    redis_url: str = Field(default="redis://localhost:6379/0")

    jwt_secret_key: str = Field(default="replace-me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_minutes: int = Field(default=10080)
    otp_hmac_key: str = Field(default="replace-me-otp")

    password_hash_iterations: int = Field(default=240000)

    otp_code_length: int = Field(default=6)
    otp_ttl_minutes: int = Field(default=10)
    otp_max_attempts: int = Field(default=5)

    email_provider: str = Field(default="console")
    email_from: str = Field(default="noreply@election-system.local")
    resend_api_key: str = Field(default="")
    resend_api_url: str = Field(default="https://api.resend.com/emails")

    smtp_host: str = Field(default="localhost")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_use_tls: bool = Field(default=True)

    telegram_provider: str = Field(default="console")
    telegram_bot_token: str = Field(default="")
    telegram_api_base_url: str = Field(default="https://api.telegram.org")

    @field_validator("jwt_algorithm")
    @classmethod
    def _validate_jwt_algorithm(cls, v: str) -> str:
        if v not in _ALLOWED_JWT_ALGORITHMS:
            raise ValueError(
                f"jwt_algorithm must be one of {sorted(_ALLOWED_JWT_ALGORITHMS)}, got {v!r}"
            )
        return v

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        is_dev = self.app_env.lower() in _DEV_ENVS
        if not is_dev and self.jwt_secret_key in _INSECURE_JWT_DEFAULTS:
            raise ValueError(
                "jwt_secret_key must be set to a strong secret in non-development environments. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if not is_dev and len(self.jwt_secret_key) < 32:
            raise ValueError(
                "jwt_secret_key must be at least 32 characters in non-development environments."
            )
        if not is_dev and self.otp_hmac_key in _INSECURE_JWT_DEFAULTS:
            raise ValueError(
                "otp_hmac_key must be set to a strong secret in non-development environments."
            )
        if not is_dev and len(self.otp_hmac_key) < 32:
            raise ValueError(
                "otp_hmac_key must be at least 32 characters in non-development environments."
            )
        return self

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

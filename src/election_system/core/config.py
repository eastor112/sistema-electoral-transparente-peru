from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

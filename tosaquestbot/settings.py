from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class HTTPSettings(BaseSettings):
    """HTTP settings."""

    base_url: str
    host: str
    port: int


class Settings(BaseSettings):
    """Application settings."""

    db_url: PostgresDsn
    bot_token: str
    bot_admins: list[int]
    http: HTTPSettings

    class Config:  # noqa: D106
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"

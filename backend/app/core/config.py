from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DevPulse API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "postgresql://user:password@localhost:5432/devpulse"
    redis_url: str = "redis://localhost:6379"

    anthropic_api_key: str = ""

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()

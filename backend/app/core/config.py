# Central app configuration, read once at import time from environment
# variables / the .env file. Every other module imports `settings` from here
# instead of calling os.environ directly.
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DevPulse API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "postgresql://user:password@localhost:5432/devpulse"
    redis_url: str = "redis://localhost:6379"

    anthropic_api_key: str = ""  # empty = AI recommendations step is skipped

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Comma-separated list of frontend URLs allowed to call this API (CORS —
    # Cross-Origin Resource Sharing, the browser's own rule that a webpage
    # can only talk to a different website if that website explicitly says
    # "yes, this page is allowed to call me"). Defaults to just the local
    # Next.js dev server; a real deployment sets ALLOWED_ORIGINS to the
    # production frontend's URL (e.g. https://devpulse.vercel.app) instead
    # of needing a code change — see DEPLOYMENT.md.
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()

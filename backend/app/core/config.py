import os
from pathlib import Path


def _load_dotenv() -> None:
    """Read a small local .env file without overriding process environment."""
    env_file = Path(".env")
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        if key and key.replace("_", "").isalnum():
            os.environ.setdefault(key, value)


_load_dotenv()


class Settings:
    # Environment configuration avoids requiring a second settings framework.
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aquashield.db")
    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "https://aqua-shield-orcin.vercel.app,https://aqua-shield.vercel.app,"
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    )
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "20"))
    max_upload_rows: int = int(os.getenv("MAX_UPLOAD_ROWS", "200000"))

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

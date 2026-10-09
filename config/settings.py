"""Environment-based configuration. Credentials come from env vars / a git-ignored .env file."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://rahulshettyacademy.com/client").rstrip("/")
    api_url: str = os.getenv("API_URL", "https://rahulshettyacademy.com/api/ecom").rstrip("/")
    user_email: str = os.getenv("USER_EMAIL", "")
    user_password: str = os.getenv("USER_PASSWORD", "")


settings = Settings()

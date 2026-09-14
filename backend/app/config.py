"""Configuration read from environment variables."""

from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    allow_custom_provider: bool


def get_settings() -> Settings:
    # This location works whether uvicorn is launched from backend/ or the repo root.
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    return Settings(
        openai_api_key=getenv("OPENAI_API_KEY"),
        openai_model=getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        allow_custom_provider=getenv("ALLOW_CUSTOM_PROVIDER", "false").lower() == "true",
    )

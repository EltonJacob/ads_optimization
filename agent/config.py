"""Central configuration handling with python-dotenv support."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def load_environment(dotenv_path: Optional[Path] = None) -> None:
    """Load environment variables from .env without overriding existing values."""
    load_dotenv(dotenv_path or DEFAULT_ENV_FILE, override=False)


@dataclass
class Settings:
    """Container for typed configuration."""

    database_url: str = "sqlite:///amazon_ppc.db"
    amazon_ads_client_id: str = ""
    amazon_ads_client_secret: str = ""
    amazon_ads_refresh_token: str = ""
    amazon_ads_api_base: str = "https://advertising-api.amazon.com"
    amazon_ads_auth_url: str = "https://api.amazon.com/auth/o2/token"
    target_acos: float = 0.25
    min_bid: float = 0.2
    max_bid: float = 1.6
    timezone: str = "America/Chicago"
    log_level: str = "INFO"
    optimize_default_mode: str = "dry-run"
    optimize_default_window: int = 7
    fetch_rate_limit_per_sec: float = 5.0
    fetch_max_retries: int = 3
    fetch_backoff_seconds: float = 1.0
    fetch_poll_timeout_seconds: float = 600.0


def load_settings(dotenv_path: Optional[Path] = None) -> Settings:
    """Load .env values then return a Settings instance."""
    load_environment(dotenv_path)
    return Settings(
        database_url=os.getenv("DATABASE_URL", Settings.database_url),
        amazon_ads_client_id=os.getenv("AMAZON_ADS_CLIENT_ID", ""),
        amazon_ads_client_secret=os.getenv("AMAZON_ADS_CLIENT_SECRET", ""),
        amazon_ads_refresh_token=os.getenv("AMAZON_ADS_REFRESH_TOKEN", ""),
        amazon_ads_api_base=os.getenv(
            "AMAZON_ADS_API_BASE",
            Settings.amazon_ads_api_base,
        ),
        amazon_ads_auth_url=os.getenv(
            "AMAZON_ADS_AUTH_URL",
            Settings.amazon_ads_auth_url,
        ),
        target_acos=float(os.getenv("TARGET_ACOS", str(Settings.target_acos))),
        min_bid=float(os.getenv("MIN_BID", str(Settings.min_bid))),
        max_bid=float(os.getenv("MAX_BID", str(Settings.max_bid))),
        timezone=os.getenv("TZ", Settings.timezone),
        log_level=os.getenv("LOG_LEVEL", Settings.log_level),
        optimize_default_mode=os.getenv("OPTIMIZE_DEFAULT_MODE", Settings.optimize_default_mode),
        optimize_default_window=int(
            os.getenv("OPTIMIZE_DEFAULT_WINDOW", str(Settings.optimize_default_window))
        ),
        fetch_rate_limit_per_sec=float(
            os.getenv("FETCH_RATE_LIMIT_PER_SEC", str(Settings.fetch_rate_limit_per_sec))
        ),
        fetch_max_retries=int(
            os.getenv("FETCH_MAX_RETRIES", str(Settings.fetch_max_retries))
        ),
        fetch_backoff_seconds=float(
            os.getenv("FETCH_BACKOFF_SECONDS", str(Settings.fetch_backoff_seconds))
        ),
        fetch_poll_timeout_seconds=float(
            os.getenv("FETCH_POLL_TIMEOUT_SECONDS", str(Settings.fetch_poll_timeout_seconds))
        ),
    )


# Load on import so `agent.settings` is ready for use.
settings = load_settings()

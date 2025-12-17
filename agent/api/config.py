"""Configuration management for Amazon Ads API.

Loads settings from environment variables with fallback to .env file.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)


class AmazonAdsConfig:
    """Amazon Ads API configuration settings."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Required credentials
        self.client_id = os.getenv("AMAZON_ADS_CLIENT_ID")
        self.client_secret = os.getenv("AMAZON_ADS_CLIENT_SECRET")
        self.refresh_token = os.getenv("AMAZON_ADS_REFRESH_TOKEN")
        self.profile_id = os.getenv("AMAZON_ADS_PROFILE_ID")

        # API endpoints
        self.api_base = os.getenv("AMAZON_ADS_API_BASE", "https://advertising-api.amazon.com")
        self.auth_url = os.getenv("AMAZON_ADS_AUTH_URL", "https://api.amazon.com/auth/o2/token")

        # Rate limiting and retry settings
        self.rate_limit_per_sec = float(os.getenv("FETCH_RATE_LIMIT_PER_SEC", "5.0"))
        self.max_retries = int(os.getenv("FETCH_MAX_RETRIES", "3"))
        self.backoff_seconds = float(os.getenv("FETCH_BACKOFF_SECONDS", "1.0"))
        self.poll_timeout_seconds = float(os.getenv("FETCH_POLL_TIMEOUT_SECONDS", "600.0"))

        # Validate required settings
        self._validate()

    def _validate(self):
        """Validate that required configuration is present."""
        required = {
            "AMAZON_ADS_CLIENT_ID": self.client_id,
            "AMAZON_ADS_CLIENT_SECRET": self.client_secret,
            "AMAZON_ADS_REFRESH_TOKEN": self.refresh_token,
        }

        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required Amazon Ads API configuration: {', '.join(missing)}. "
                f"Please set these in your .env file."
            )

    @property
    def is_configured(self) -> bool:
        """Check if all required configuration is present."""
        return all([
            self.client_id,
            self.client_secret,
            self.refresh_token,
        ])


# Global config instance
config = AmazonAdsConfig()

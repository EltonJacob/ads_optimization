"""Amazon Ads API health check and profile listing."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def run() -> List[Dict[str, Any]]:
    """Check Amazon Ads API connection and list available profiles.

    Returns:
        List of profile dictionaries with id, name, marketplace, etc.
    """
    logger.info("Running Amazon Ads API health check")

    # Placeholder: Would actually call Amazon Ads API here
    # For now, return mock data
    profiles = [
        {
            "profile_id": "12345678",
            "name": "Test Profile - US",
            "marketplace": "US",
            "country_code": "US",
            "currency_code": "USD",
            "type": "seller"
        }
    ]

    logger.info(f"Health check complete: {len(profiles)} profiles found")
    return profiles


def print_profiles(profiles: List[Dict[str, Any]]) -> None:
    """Print profiles in a formatted way for CLI output."""
    if not profiles:
        print("⚠️  No profiles found")
        return

    print(f"\n✓ Found {len(profiles)} Amazon Ads profile(s):\n")
    for profile in profiles:
        print(f"  Profile ID: {profile.get('profile_id')}")
        print(f"  Name:       {profile.get('name')}")
        print(f"  Marketplace: {profile.get('marketplace')} ({profile.get('country_code')})")
        print(f"  Currency:   {profile.get('currency_code')}")
        print(f"  Type:       {profile.get('type')}")
        print()

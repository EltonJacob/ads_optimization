"""Generate mock performance data for testing purposes."""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def run(days: int = 30, job_id: Optional[str] = None) -> None:
    """Generate mock performance data for testing.

    This is a placeholder for generating test data.
    Will be implemented when we have the database models.
    """
    logger.info(f"Mock data generation requested for last {days} days")
    print(f"⚠️  Mock data generation not yet implemented")
    print(f"   Job ID: {job_id}")
    print(f"   Would generate {days} days of test data")

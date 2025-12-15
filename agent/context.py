"""Application context and utilities."""

from __future__ import annotations

import uuid
from datetime import datetime


def generate_job_id(prefix: str = "job") -> str:
    """Generate a unique job ID with timestamp and UUID.

    Args:
        prefix: Prefix for the job ID (e.g., 'fetch', 'import', 'optimize')

    Returns:
        Unique job ID string like 'fetch_20251215_1234_abc123'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}"

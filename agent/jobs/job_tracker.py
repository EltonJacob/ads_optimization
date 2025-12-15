"""In-memory job status tracking for async operations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class JobStatus(str, Enum):
    """Status of async jobs."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class JobInfo:
    """Information about a running or completed job."""
    job_id: str
    job_type: str
    status: JobStatus
    progress: float = 0.0  # 0-100
    records_fetched: int = 0
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "progress": self.progress,
            "records_fetched": self.records_fetched,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


class JobTracker:
    """In-memory storage for job status tracking."""

    def __init__(self):
        self._jobs: Dict[str, JobInfo] = {}
        self._lock = asyncio.Lock()

    async def create_job(
        self,
        job_id: str,
        job_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JobInfo:
        """Create a new job entry."""
        async with self._lock:
            job = JobInfo(
                job_id=job_id,
                job_type=job_type,
                status=JobStatus.PENDING,
                metadata=metadata or {}
            )
            self._jobs[job_id] = job
            return job

    async def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Retrieve job information."""
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[float] = None,
        records_fetched: Optional[int] = None,
        error: Optional[str] = None,
    ) -> Optional[JobInfo]:
        """Update job status."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            if status is not None:
                job.status = status
                if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.TIMEOUT):
                    job.completed_at = datetime.now()

            if progress is not None:
                job.progress = max(0.0, min(100.0, progress))

            if records_fetched is not None:
                job.records_fetched = records_fetched

            if error is not None:
                job.errors.append(error)

            return job

    async def list_jobs(self, job_type: Optional[str] = None) -> list[JobInfo]:
        """List all jobs, optionally filtered by type."""
        async with self._lock:
            jobs = list(self._jobs.values())
            if job_type:
                jobs = [j for j in jobs if j.job_type == job_type]
            return sorted(jobs, key=lambda j: j.started_at, reverse=True)

    async def cleanup_old_jobs(self, keep_last_n: int = 100) -> int:
        """Remove old completed jobs, keeping only the most recent N."""
        async with self._lock:
            jobs = sorted(
                self._jobs.values(),
                key=lambda j: j.started_at,
                reverse=True
            )

            if len(jobs) <= keep_last_n:
                return 0

            to_remove = jobs[keep_last_n:]
            removed = 0
            for job in to_remove:
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    del self._jobs[job.job_id]
                    removed += 1

            return removed


# Global job tracker instance
_tracker: Optional[JobTracker] = None


def get_tracker() -> JobTracker:
    """Get or create the global job tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = JobTracker()
    return _tracker
